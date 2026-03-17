"""Heuristic auto-detection for generic article extraction."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag
import structlog

from app.core.scraping.engine import ScrapingEngine

logger = structlog.get_logger()

ARTICLE_TYPES = {"article", "blogposting", "newsarticle"}
CONTAINER_HINTS = ["post", "article", "card", "item", "entry", "blog"]


@dataclass
class AutoDetectResult:
    url: str
    item_selector: str
    fields: list[dict]
    confidence: float
    pagination_type: str
    pagination_selector: str | None
    detected_via: str
    preview_items: list[dict]


class AutoDetector:
    def __init__(self, url: str, html: str):
        self.url = url
        self.html = html
        self.soup = BeautifulSoup(html or "", "html.parser")

    def detect(self) -> dict[str, Any]:
        """Analyze a page and return a best-effort extraction config."""
        candidates = []
        for strategy in (
            self._detect_json_ld,
            self._detect_open_graph,
            self._detect_rss,
            self._detect_structural,
        ):
            try:
                candidates.append(strategy())
            except Exception as e:
                logger.warning("auto_detect_strategy_failed", strategy=strategy.__name__, url=self.url, error=str(e))
        valid_candidates = [candidate for candidate in candidates if candidate is not None]

        if not valid_candidates:
            result = AutoDetectResult(
                url=self.url,
                item_selector="article",
                fields=[],
                confidence=0.0,
                pagination_type="none",
                pagination_selector=None,
                detected_via="none",
                preview_items=[],
            )
            return asdict(result)

        best = max(valid_candidates, key=lambda candidate: candidate.confidence)
        if best.fields:
            best.preview_items = self._build_preview(best.item_selector, best.fields)
        return asdict(best)

    def _detect_json_ld(self) -> AutoDetectResult | None:
        scripts = self.soup.find_all("script", attrs={"type": "application/ld+json"})
        for script in scripts:
            try:
                payload = json.loads(script.get_text(strip=True) or "null")
            except Exception:
                continue

            objects = self._flatten_json_ld(payload)
            article_objects = [obj for obj in objects if self._is_article_like(obj)]
            item_list_objects = [obj for obj in objects if self._is_item_list_like(obj)]

            if article_objects:
                fields = self._fields_from_json_ld(article_objects[0])
                if fields:
                    return AutoDetectResult(
                        url=self.url,
                        item_selector="html",
                        fields=fields,
                        confidence=0.95,
                        pagination_type="none",
                        pagination_selector=None,
                        detected_via="json-ld",
                        preview_items=[],
                    )

            if item_list_objects:
                item_list = item_list_objects[0]
                entries = item_list.get("itemListElement") or []
                first_item = None
                for entry in entries:
                    if isinstance(entry, dict):
                        first_item = entry.get("item") or entry
                        if isinstance(first_item, dict):
                            break
                if first_item:
                    fields = self._fields_from_json_ld(first_item)
                    if fields:
                        return AutoDetectResult(
                            url=self.url,
                            item_selector="html",
                            fields=fields,
                            confidence=0.95,
                            pagination_type="none",
                            pagination_selector=None,
                            detected_via="json-ld",
                            preview_items=[],
                        )
        return None

    def _detect_open_graph(self) -> AutoDetectResult | None:
        og_data = {}
        for meta in self.soup.find_all("meta"):
            prop = meta.get("property") or meta.get("name")
            if prop and prop.startswith("og:"):
                og_data[prop] = meta.get("content")

        if not og_data:
            return None

        if self.soup.find_all("article") and len(self.soup.find_all("article")) > 1:
            return None

        fields = []
        mapping = {
            "title": "og:title",
            "url": "og:url",
            "description": "og:description",
            "image": "og:image",
            "site_name": "og:site_name",
        }
        for name, og_key in mapping.items():
            if og_data.get(og_key):
                fields.append(self._make_field(name=name, selector=f'meta[property="{og_key}"]', attribute="content", required=name in {"title", "url"}, transform="to_absolute_url" if name in {"url", "image"} else None))

        if not fields:
            return None

        return AutoDetectResult(
            url=self.url,
            item_selector="html",
            fields=fields,
            confidence=0.7,
            pagination_type="none",
            pagination_selector=None,
            detected_via="open-graph",
            preview_items=[],
        )

    def _detect_rss(self) -> AutoDetectResult | None:
        feed_link = None
        for link in self.soup.find_all("link", rel="alternate"):
            feed_type = link.get("type", "")
            if feed_type in {"application/rss+xml", "application/atom+xml"}:
                feed_link = link.get("href")
                if feed_link:
                    break

        if not feed_link:
            return None

        feed_url = urljoin(self.url, feed_link)
        try:
            response = httpx.get(feed_url, follow_redirects=True, timeout=10.0)
            response.raise_for_status()
            feed_soup = BeautifulSoup(response.text, "xml")
        except Exception as e:
            logger.warning("rss_feed_fetch_failed", url=feed_url, error=str(e))
            return None

        items = feed_soup.find_all(["item", "entry"])
        if not items:
            return None

        preview_items = []
        for item in items[:3]:
            preview_items.append({
                "title": self._xml_text(item, ["title"]),
                "url": self._xml_text(item, ["link", "id"]),
                "description": self._xml_text(item, ["description", "summary"]),
                "date": self._xml_text(item, ["pubDate", "published", "updated"]),
            })

        return AutoDetectResult(
            url=self.url,
            item_selector="rss:item",
            fields=[],
            confidence=0.9,
            pagination_type="none",
            pagination_selector=None,
            detected_via="rss",
            preview_items=preview_items,
        )

    def _detect_structural(self) -> AutoDetectResult | None:
        candidates: list[tuple[str, list[Tag]]] = []

        article_tags = self.soup.find_all("article")
        if len(article_tags) >= 1:
            candidates.append(("article", article_tags))

        for hint in CONTAINER_HINTS:
            selector = f'[class*="{hint}"]'
            matches = self.soup.select(selector)
            if len(matches) >= 3:
                candidates.append((selector, matches))

        repeated = self._repeated_structure_candidates()
        candidates.extend(repeated)

        best_result = None
        best_score = -1
        for selector, containers in candidates:
            fields = self._infer_fields_for_container(containers[0]) if containers else []
            score = len(fields)
            if score > best_score and fields:
                confidence = min(0.3 + score * 0.08, 0.7)
                pagination_selector = self._detect_pagination_selector()
                best_result = AutoDetectResult(
                    url=self.url,
                    item_selector=selector,
                    fields=fields,
                    confidence=confidence,
                    pagination_type="next_link" if pagination_selector else "none",
                    pagination_selector=pagination_selector,
                    detected_via="structural",
                    preview_items=[],
                )
                best_score = score

        return best_result

    def _flatten_json_ld(self, payload: Any) -> list[dict[str, Any]]:
        objects: list[dict[str, Any]] = []
        stack = payload if isinstance(payload, list) else [payload]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                objects.append(current)
                graph = current.get("@graph")
                if isinstance(graph, list):
                    stack.extend(graph)
            elif isinstance(current, list):
                stack.extend(current)
        return objects

    def _is_article_like(self, obj: dict[str, Any]) -> bool:
        obj_type = obj.get("@type")
        if isinstance(obj_type, list):
            return any(str(item).lower() in ARTICLE_TYPES for item in obj_type)
        return str(obj_type).lower() in ARTICLE_TYPES

    def _is_item_list_like(self, obj: dict[str, Any]) -> bool:
        obj_type = obj.get("@type")
        if isinstance(obj_type, list):
            return any(str(item).lower() in {"itemlist", "webpage"} for item in obj_type)
        return str(obj_type).lower() in {"itemlist", "webpage"}

    def _fields_from_json_ld(self, obj: dict[str, Any]) -> list[dict[str, Any]]:
        field_map = {
            "title": ["headline", "name"],
            "url": ["url", "@id"],
            "author": ["author"],
            "date": ["datePublished"],
            "description": ["description"],
        }
        fields = []
        for name, keys in field_map.items():
            for key in keys:
                if key == "author":
                    author = obj.get("author")
                    if isinstance(author, dict) and author.get("name"):
                        fields.append(self._json_ld_script_field(name, key_path='author.name', required=False))
                        break
                    if isinstance(author, list):
                        first = next((entry for entry in author if isinstance(entry, dict) and entry.get("name")), None)
                        if first:
                            fields.append(self._json_ld_script_field(name, key_path='author.name', required=False))
                            break
                    continue
                if obj.get(key):
                    transform = "parse_date" if name == "date" else "to_absolute_url" if name == "url" else None
                    fields.append(self._json_ld_script_field(name, key_path=key, required=name in {"title", "url"}, transform=transform))
                    break
        return fields

    def _json_ld_script_field(
        self,
        name: str,
        key_path: str,
        required: bool,
        transform: str | None = None,
    ) -> dict[str, Any]:
        return self._make_field(
            name=name,
            selector=f'//script[@type="application/ld+json"]',
            attribute=f'json_ld:{key_path}',
            required=required,
            transform=transform,
        )

    def _repeated_structure_candidates(self) -> list[tuple[str, list[Tag]]]:
        candidates: list[tuple[str, list[Tag]]] = []
        seen: set[str] = set()
        for tag_name in ("li", "div"):
            for tag in self.soup.find_all(tag_name):
                classes = tag.get("class") or []
                if not classes:
                    continue
                selector = f'{tag_name}.{".".join(classes[:2])}'
                if selector in seen:
                    continue
                matches = self.soup.select(selector)
                if len(matches) >= 3:
                    candidates.append((selector, matches))
                    seen.add(selector)
        return candidates

    def _infer_fields_for_container(self, container: Tag) -> list[dict[str, Any]]:
        fields = []

        title_selector = self._first_matching_selector(container, ["h1", "h2", "h3", ".title", ".heading"])
        if title_selector:
            fields.append(self._make_field("title", title_selector, transform="strip"))

        link_selector = self._first_matching_selector(container, ["a[href]"])
        if link_selector:
            fields.append(self._make_field("url", link_selector, attribute="href", transform="to_absolute_url"))

        author_selector = self._find_class_based_selector(container, ["author", "by-line", "byline"])
        if author_selector:
            fields.append(self._make_field("author", author_selector, required=False, transform="strip"))

        date_selector = self._first_matching_selector(container, ["time", ".date", ".published", ".time"])
        if date_selector:
            attribute = "datetime" if container.select_one("time") else None
            fields.append(self._make_field("date", date_selector, attribute=attribute, required=False, transform="parse_date"))

        image_selector = self._first_matching_selector(container, ["img"])
        if image_selector:
            fields.append(self._make_field("image", image_selector, attribute="src", required=False, transform="to_absolute_url"))

        description_selector = self._first_matching_selector(container, [".description", ".summary", "p"])
        if description_selector:
            fields.append(self._make_field("description", description_selector, required=False, transform="strip"))

        return fields

    def _first_matching_selector(self, container: Tag, candidates: list[str]) -> str | None:
        for selector in candidates:
            try:
                match = container.select_one(selector)
            except Exception:
                continue
            if match is not None:
                return self._selector_for_element(match)
        return None

    def _find_class_based_selector(self, container: Tag, hints: list[str]) -> str | None:
        for element in container.find_all(True):
            classes = element.get("class") or []
            joined = " ".join(classes).lower()
            text = element.get_text(" ", strip=True).lower()
            if any(hint in joined or hint in text for hint in hints):
                return self._selector_for_element(element)
        return None

    def _selector_for_element(self, element: Tag) -> str:
        if element.get("id"):
            return f'#{element.get("id")}'

        classes = [cls for cls in (element.get("class") or []) if cls]
        if classes:
            return f'{element.name}.{".".join(classes[:2])}'
        return element.name

    def _detect_pagination_selector(self) -> str | None:
        candidates = [
            'a[rel="next"]',
            'link[rel="next"]',
            'a.next',
            'a[class*="next"]',
            'a[aria-label*="Next"]',
        ]
        for selector in candidates:
            try:
                if self.soup.select_one(selector) is not None:
                    return selector
            except Exception:
                continue
        return None

    def _make_field(
        self,
        name: str,
        selector: str,
        attribute: str | None = None,
        transform: str | None = None,
        required: bool = True,
        default_value: str | None = None,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "selector": selector,
            "attribute": attribute,
            "transform": transform,
            "required": required,
            "default_value": default_value,
        }

    def _build_preview(self, item_selector: str, fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not fields:
            return []

        try:
            engine = ScrapingEngine({
                "base_url": self.url,
                "item_selector": item_selector,
                "fields": fields,
                "pagination_type": "none",
                "max_pages": 1,
                "request_delay_ms": 0,
                "custom_headers": None,
                "use_headless_browser": False,
            })
            items = engine._extract_items(self.soup, self.url)
            return [item["data"] for item in items[:3]]
        except Exception as e:
            logger.warning("auto_detect_preview_failed", url=self.url, error=str(e))
            return []

    def _xml_text(self, item: Tag, names: list[str]) -> str | None:
        for name in names:
            node = item.find(name)
            if node is not None:
                if name == "link" and node.get("href"):
                    return node.get("href")
                text = node.get_text(strip=True)
                if text:
                    return text
        return None
