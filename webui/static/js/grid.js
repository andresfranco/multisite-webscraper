// ===================================
// Grid Page JavaScript
// Enhanced with Multiple Filters & Pagination
// ===================================

const authorInput = document.getElementById("authorInput");
const dateFromInput = document.getElementById("dateFromInput");
const dateToInput = document.getElementById("dateToInput");
const websiteInput = document.getElementById("websiteInput");
const searchBtn = document.getElementById("searchBtn");
const clearFiltersBtn = document.getElementById("clearFiltersBtn");
const articlesContainer = document.getElementById("articleGrid");
const loadingIndicator = document.getElementById("loadingIndicator");
const loadMoreContainer = document.getElementById("loadMoreContainer");
const loadMoreBtn = document.getElementById("loadMoreBtn");
const loadMoreText = document.getElementById("loadMoreText");
const resultsText = document.getElementById("resultsText");
const filterStatus = document.getElementById("filterStatus");
const filterChipsContainer = document.getElementById("filterChipsContainer");
const filterChipsDiv = document.getElementById("filterChips");

const ARTICLES_PER_LOAD = 20; // Load 20 articles at a time
let displayedArticles = []; // Articles currently displayed
let allArticles = []; // All articles from API
let activeFilters = []; // Array of active filter objects
let totalArticlesCount = 0; // Total count from API

/**
 * Filter object structure:
 * {
 *   id: unique identifier (e.g., "author", "date_range", "website"),
 *   type: filter type (author, date_range, website),
 *   label: display label (e.g., "Author: John Doe"),
 *   icon: FontAwesome icon class,
 *   value: the actual filter value,
 *   apiParam: parameter name for API (author, date_from, date_to, website)
 * }
 */

/**
 * Load articles on page load
 */
document.addEventListener("DOMContentLoaded", async () => {
  await loadFilters();
  await loadArticles();
});

/**
 * Load filter options from API
 */
async function loadFilters() {
  try {
    const response = await fetch("/api/article-filters");
    const data = await response.json();

    if (data.success && data.filters) {
      if (data.filters.min_date) {
        dateFromInput.min = data.filters.min_date;
        dateFromInput.max = data.filters.max_date;
      }
      if (data.filters.max_date) {
        dateToInput.min = data.filters.min_date;
        dateToInput.max = data.filters.max_date;
      }
    }
  } catch (error) {
    console.error("Error loading filters:", error);
  }
}

/**
 * Load articles from API with active filters
 * @param {boolean} reset - If true, reset displayed articles and load from beginning
 */
async function loadArticles(reset = false) {
  try {
    showLoading(true);

    // Reset if needed
    if (reset) {
      displayedArticles = [];
      allArticles = [];
    }

    // Build query parameters from active filters
    const params = new URLSearchParams();

    activeFilters.forEach((filter) => {
      if (filter.type === "date_range") {
        if (filter.value.from) params.append("date_from", filter.value.from);
        if (filter.value.to) params.append("date_to", filter.value.to);
      } else {
        params.append(filter.apiParam, filter.value);
      }
    });

    // Request more articles than currently displayed to check if there are more
    params.append("page", 1);
    params.append("per_page", displayedArticles.length + ARTICLES_PER_LOAD);

    const response = await fetch(`/api/articles?${params}`);
    const data = await response.json();

    if (data.success) {
      allArticles = data.articles;
      totalArticlesCount = data.total_count;

      // If reset, show first batch, otherwise add new batch
      if (reset) {
        displayedArticles = allArticles.slice(0, ARTICLES_PER_LOAD);
      } else {
        displayedArticles = allArticles;
      }

      updateStats(totalArticlesCount);
      renderArticles(displayedArticles, reset);
      updateLoadMoreButton();
      updateResultsInfo(totalArticlesCount, displayedArticles.length);
    } else {
      showError("Failed to load articles");
    }
  } catch (error) {
    console.error("Error loading articles:", error);
    showError("Error loading articles: " + error.message);
  } finally {
    showLoading(false);
  }
}

/**
 * Update results info display
 * @param {number} totalCount - Total articles matching filters
 * @param {number} displayCount - Articles currently displayed
 */
function updateResultsInfo(totalCount, displayCount) {
  if (totalCount === 0) {
    resultsText.textContent = "No articles found";
  } else {
    resultsText.textContent = `Showing ${displayCount} of ${totalCount} articles`;
  }
}

/**
 * Render filter chips from active filters
 */
function renderFilterChips() {
  filterChipsDiv.innerHTML = "";

  if (activeFilters.length === 0) {
    filterChipsContainer.style.display = "none";
    return;
  }

  filterChipsContainer.style.display = "flex";

  activeFilters.forEach((filter) => {
    const chip = document.createElement("div");
    chip.className = "filter-chip";
    chip.setAttribute("data-filter-id", filter.id);

    let displayLabel = filter.label;

    // Create chip content
    const chipContent = document.createElement("span");
    chipContent.className = "filter-chip-icon";
    chipContent.innerHTML = `<i class="${filter.icon}"></i>`;

    const chipText = document.createElement("span");
    chipText.className = "filter-chip-text";
    chipText.textContent = displayLabel;
    chipText.title = displayLabel; // Tooltip on hover

    const removeBtn = document.createElement("button");
    removeBtn.className = "filter-chip-remove";
    removeBtn.setAttribute("type", "button");
    removeBtn.setAttribute("aria-label", `Remove ${filter.label} filter`);
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      removeFilter(filter.id);
    });

    chip.appendChild(chipContent);
    chip.appendChild(chipText);
    chip.appendChild(removeBtn);

    filterChipsDiv.appendChild(chip);
  });
}

/**
 * Add a filter to the active filters list
 * @param {string} type - Filter type (author, date_range, website)
 * @param {string|object} value - Filter value
 * @param {string} label - Display label for the chip
 * @param {string} icon - FontAwesome icon class
 * @param {string} apiParam - API parameter name
 */
function addFilter(type, value, label, icon, apiParam) {
  // Generate unique ID
  const id = `${type}-${Date.now()}`;

  // Check if filter of same type already exists and replace it
  const existingIndex = activeFilters.findIndex((f) => f.type === type);
  const filterObj = {
    id,
    type,
    label,
    icon,
    value,
    apiParam,
  };

  if (existingIndex !== -1) {
    activeFilters[existingIndex] = filterObj;
  } else {
    activeFilters.push(filterObj);
  }

  renderFilterChips();
  loadArticles(true); // Reset and load from beginning
}

/**
 * Remove a filter by ID
 * @param {string} filterId - Filter ID to remove
 */
function removeFilter(filterId) {
  const filterIndex = activeFilters.findIndex((f) => f.id === filterId);

  if (filterIndex !== -1) {
    const removedFilter = activeFilters[filterIndex];

    // Clear the corresponding input field
    if (removedFilter.type === "author") {
      authorInput.value = "";
    } else if (removedFilter.type === "date_range") {
      dateFromInput.value = "";
      dateToInput.value = "";
    } else if (removedFilter.type === "website") {
      websiteInput.value = "";
    }

    activeFilters.splice(filterIndex, 1);
    renderFilterChips();
    loadArticles(true); // Reset and load from beginning
  }
}

/**
 * Clear all active filters
 */
function clearAllFilters() {
  activeFilters = [];
  authorInput.value = "";
  dateFromInput.value = "";
  dateToInput.value = "";
  websiteInput.value = "";
  renderFilterChips();
  loadArticles(true); // Reset and load from beginning
}

/**
 * Update statistics display
 * @param {number} totalCount - Total articles in database
 */
function updateStats(totalCount) {
  document.getElementById("totalCount").textContent = totalCount;

  // Count unique authors from all articles
  fetch("/api/article-filters")
    .then((r) => r.json())
    .then((data) => {
      if (data.success && data.filters && data.filters.authors) {
        document.getElementById("authorCount").textContent =
          data.filters.authors.filter((a) => a !== "Unknown").length;
      }
    })
    .catch((e) => console.error("Error updating author count:", e));

  document.getElementById("footerCount").textContent = totalCount;
}

/**
 * Render articles to the grid
 * @param {Array} articles - Array of article objects to render
 * @param {boolean} replace - If true, replace all articles; if false, append
 */
function renderArticles(articles, replace = true) {
  if (articles.length === 0 && replace) {
    articlesContainer.innerHTML = `
      <div style="grid-column: 1/-1;">
        <div class="empty-state">
          <div class="empty-state-icon"><i class="fas fa-inbox"></i></div>
          <div class="empty-state-title">No Articles Found</div>
          <div class="empty-state-text">
            ${getEmptyStateMessage()}
          </div>
          <a href="/" class="btn btn-primary">
            <i class="fas fa-search"></i> Start Scraping
          </a>
        </div>
      </div>
    `;
    return;
  }

  const articlesHTML = articles
    .map(
      (article) => `
      <div class="card" data-article-id="${article.id}">
        <div class="card-header">
          <h3 class="card-title">${escapeHtml(article.title)}</h3>
        </div>
        <div class="card-body">
          <div class="card-meta">
            <div class="meta-item">
              <span class="meta-icon"><i class="fas fa-pen-fancy"></i></span>
              <div>
                <div class="meta-label">Author</div>
                <div class="meta-value">${escapeHtml(article.author)}</div>
              </div>
            </div>
            <div class="meta-item">
              <span class="meta-icon"><i class="fas fa-calendar-alt"></i></span>
              <div>
                <div class="meta-label">Date</div>
                <div class="meta-value">${escapeHtml(formatDate(article.date))}</div>
              </div>
            </div>
            <div class="meta-item">
              <span class="meta-icon"><i class="fas fa-globe"></i></span>
              <div>
                <div class="meta-label">Source</div>
                <div class="meta-value">${escapeHtml(article.website_url)}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="card-link">
            <i class="fas fa-external-link-alt"></i> Read Article
          </a>
        </div>
      </div>
    `,
    )
    .join("");

  if (replace) {
    articlesContainer.innerHTML = articlesHTML;
  } else {
    articlesContainer.insertAdjacentHTML("beforeend", articlesHTML);
  }
}

/**
 * Get appropriate empty state message
 * @returns {string} Empty state message
 */
function getEmptyStateMessage() {
  if (activeFilters.length > 0) {
    return "No articles match your filters. Try adjusting your search criteria.";
  }
  return "Start scraping to collect articles from your favorite sources";
}

/**
 * Update Load More button visibility and text
 */
function updateLoadMoreButton() {
  const hasMore = displayedArticles.length < totalArticlesCount;

  if (hasMore && totalArticlesCount > 0) {
    loadMoreContainer.style.display = "block";
    loadMoreText.textContent = `Showing ${displayedArticles.length} of ${totalArticlesCount} articles`;
    loadMoreBtn.disabled = false;
  } else {
    loadMoreContainer.style.display = "none";
  }
}

/**
 * Load more articles (next batch)
 */
async function loadMoreArticles() {
  try {
    loadMoreBtn.disabled = true;
    loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

    // Load next batch
    await loadArticles(false);

    // Scroll smoothly to the first new article
    const cards = document.querySelectorAll(".card");
    if (cards.length > displayedArticles.length - ARTICLES_PER_LOAD) {
      const firstNewCard = cards[displayedArticles.length - ARTICLES_PER_LOAD];
      if (firstNewCard) {
        firstNewCard.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    loadMoreBtn.innerHTML =
      '<i class="fas fa-plus-circle"></i> Load More Articles';
  } catch (error) {
    console.error("Error loading more articles:", error);
    loadMoreBtn.innerHTML =
      '<i class="fas fa-plus-circle"></i> Load More Articles';
    loadMoreBtn.disabled = false;
  }
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Format date string for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
  if (!dateString || dateString === "N/A") return "N/A";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch (_) {
    return dateString;
  }
}

/**
 * Show or hide loading indicator
 * @param {boolean} show - True to show, false to hide
 */
function showLoading(show) {
  loadingIndicator.style.display = show ? "block" : "none";
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i><span>${escapeHtml(message)}</span>`;
  const container = document.querySelector(".container");
  const searchBox = document.querySelector(".search-box");
  container.insertBefore(errorDiv, searchBox.nextSibling);

  // Auto-remove error after 5 seconds
  setTimeout(() => {
    errorDiv.remove();
  }, 5000);
}

// Event Listeners

/**
 * Search button event - Add filters when explicitly clicked
 */
searchBtn.addEventListener("click", () => {
  const authorValue = authorInput.value.trim();
  const dateFromValue = dateFromInput.value.trim();
  const dateToValue = dateToInput.value.trim();
  const websiteValue = websiteInput.value.trim();

  // Remove existing filters of these types
  activeFilters = activeFilters.filter(
    (f) => !["author", "date_range", "website"].includes(f.type),
  );

  // Add new filters if they have values
  if (authorValue) {
    addFilter(
      "author",
      authorValue,
      `Author: "${authorValue}"`,
      "fas fa-pen-fancy",
      "author",
    );
  } else if (dateFromValue || dateToValue) {
    const dateLabel =
      dateFromValue && dateToValue
        ? `Date: ${dateFromValue} to ${dateToValue}`
        : dateFromValue
          ? `Date: From ${dateFromValue}`
          : `Date: Until ${dateToValue}`;

    addFilter(
      "date_range",
      { from: dateFromValue, to: dateToValue },
      dateLabel,
      "fas fa-calendar-alt",
      "date_range",
    );
  } else if (websiteValue) {
    addFilter(
      "website",
      websiteValue,
      `Website: "${websiteValue}"`,
      "fas fa-globe",
      "website",
    );
  }

  renderFilterChips();
  currentPage = 1;
  loadArticles();
});

/**
 * Clear filters button event
 */
clearFiltersBtn.addEventListener("click", () => {
  clearAllFilters();
});

/**
 * Load More button event
 */
loadMoreBtn.addEventListener("click", () => {
  loadMoreArticles();
});

/**
 * Clear all articles button
 */
document.getElementById("clearAllBtn").addEventListener("click", async () => {
  if (
    !confirm(
      "Are you sure you want to delete all articles? This cannot be undone.",
    )
  ) {
    return;
  }

  try {
    showLoading(true);
    const response = await fetch("/api/clear-articles", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      clearAllFilters();
      await loadFilters();
      await loadArticles(true);
      alert("All articles have been deleted.");
    } else {
      showError("Failed to clear articles: " + data.message);
    }
  } catch (error) {
    console.error("Error clearing articles:", error);
    showError("Error clearing articles: " + error.message);
  } finally {
    showLoading(false);
  }
});
