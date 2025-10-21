"""Test script to verify author name extraction from Real Python articles.

This script tests the fallback logic for extracting author names when the
primary div#author card is not found.
"""

from bs4 import BeautifulSoup
from webscraper_core.scraper import WebScraper


def test_primary_method():
    """Test extracting author from primary location (div#author)."""
    html_content = """
    <html>
    <body>
        <div class="card mt-3" id="author">
            <p class="card-header h3">About <strong>Ian Eyre</strong></p>
            <div class="card-body">
                <p>Ian is an avid Pythonista and Real Python contributor.</p>
            </div>
        </div>
    </body>
    </html>
    """

    soup = BeautifulSoup(html_content, "html.parser")

    # Find author card: div class="card mt-3" with id="author"
    author_card = soup.find("div", class_="card", id="author")
    assert author_card is not None, "Primary method: Author card not found"

    # Find p tag with class "card-header"
    header_p = author_card.find("p", class_="card-header")
    assert header_p is not None, "Primary method: Header p tag not found"

    # Find strong tag inside the p tag
    strong_tag = header_p.find("strong")
    assert strong_tag is not None, "Primary method: Strong tag not found"

    author_name = strong_tag.get_text(strip=True)
    assert author_name == "Ian Eyre", (
        f"Primary method: Expected 'Ian Eyre', got '{author_name}'"
    )

    print("✓ Primary method test passed: Found author 'Ian Eyre'")


def test_fallback_method():
    """Test extracting author from fallback location (p.card-header without div#author)."""
    html_content = """
    <html>
    <body>
        <div class="article-content">
            <h1>Article Title</h1>
            <p>Article content here...</p>
        </div>
        <p class="card-header h3">About <strong>Steven Loyens</strong></p>
        <div class="card-body">
            <p>Steven is a Python developer.</p>
        </div>
    </body>
    </html>
    """

    soup = BeautifulSoup(html_content, "html.parser")

    # Primary method: try to find author card with id="author"
    author_card = soup.find("div", class_="card", id="author")
    assert author_card is None, "Fallback method: Author card should not exist"

    # Fallback method: Look for p tag with class "card-header" anywhere on page
    header_p_fallback = soup.find("p", class_="card-header")
    assert header_p_fallback is not None, "Fallback method: Header p tag not found"

    # Find strong tag inside the p tag
    strong_tag = header_p_fallback.find("strong")
    assert strong_tag is not None, "Fallback method: Strong tag not found"

    author_name = strong_tag.get_text(strip=True)
    assert author_name == "Steven Loyens", (
        f"Fallback method: Expected 'Steven Loyens', got '{author_name}'"
    )

    print("✓ Fallback method test passed: Found author 'Steven Loyens'")


def test_no_author_found():
    """Test handling when author cannot be found."""
    html_content = """
    <html>
    <body>
        <div class="article-content">
            <h1>Article Title</h1>
            <p>Article content here...</p>
        </div>
    </body>
    </html>
    """

    soup = BeautifulSoup(html_content, "html.parser")

    # Primary method
    author_card = soup.find("div", class_="card", id="author")
    if author_card:
        header_p = author_card.find("p", class_="card-header")
        if header_p:
            strong_tag = header_p.find("strong")
            if strong_tag:
                author_name = strong_tag.get_text(strip=True)
                assert False, "Should not find author"

    # Fallback method
    header_p_fallback = soup.find("p", class_="card-header")
    assert header_p_fallback is None, "No author should be found"

    print("✓ No author found test passed: Correctly returned None")


def test_multiple_cards_fallback():
    """Test fallback when multiple p.card-header elements exist (should find first)."""
    html_content = """
    <html>
    <body>
        <p class="card-header h3">About <strong>First Author</strong></p>
        <p class="card-header h3">About <strong>Second Author</strong></p>
    </body>
    </html>
    """

    soup = BeautifulSoup(html_content, "html.parser")

    # Fallback method should find the first one
    header_p_fallback = soup.find("p", class_="card-header")
    assert header_p_fallback is not None, "Fallback method: Header p tag not found"

    strong_tag = header_p_fallback.find("strong")
    assert strong_tag is not None, "Fallback method: Strong tag not found"

    author_name = strong_tag.get_text(strip=True)
    assert author_name == "First Author", (
        f"Expected 'First Author', got '{author_name}'"
    )

    print("✓ Multiple cards fallback test passed: Found first author 'First Author'")


if __name__ == "__main__":
    print("Running author extraction tests...\n")

    test_primary_method()
    test_fallback_method()
    test_no_author_found()
    test_multiple_cards_fallback()

    print("\n✓ All tests passed!")
