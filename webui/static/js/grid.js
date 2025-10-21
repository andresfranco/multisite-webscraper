// ===================================
// Grid Page JavaScript
// ===================================

const searchInput = document.getElementById("searchInput");
const filterButtons = document.querySelectorAll(".filter-btn");
const articlesContainer = document.getElementById("articleGrid");

let articlesData = [];

/**
 * Load articles on page load
 */
document.addEventListener("DOMContentLoaded", async () => {
  await loadArticles();
});

/**
 * Load articles from API
 */
async function loadArticles() {
  try {
    document.getElementById("loadingIndicator").style.display = "block";
    const response = await fetch("/api/articles");
    const data = await response.json();

    if (data.success) {
      articlesData = data.articles;
      updateStats();
      renderArticles(articlesData);
    } else {
      showError("Failed to load articles");
    }
  } catch (error) {
    console.error("Error loading articles:", error);
    showError("Error loading articles: " + error.message);
  } finally {
    document.getElementById("loadingIndicator").style.display = "none";
  }
}

/**
 * Update statistics display
 */
function updateStats() {
  document.getElementById("totalCount").textContent = articlesData.length;

  // Count unique authors
  const uniqueAuthors = new Set(articlesData.map((a) => a.author));
  document.getElementById("authorCount").textContent = uniqueAuthors.size;
  document.getElementById("footerCount").textContent = articlesData.length;
}

/**
 * Render articles to the grid
 * @param {Array} articles - Array of article objects to render
 */
function renderArticles(articles) {
  if (articles.length === 0) {
    articlesContainer.innerHTML = `
            <div style="grid-column: 1/-1;">
                <div class="empty-state">
                    <div class="empty-state-icon">📚</div>
                    <div class="empty-state-title">No Articles Yet</div>
                    <div class="empty-state-text">
                        No scraped articles found. Go back to the home page and start scraping!
                    </div>
                    <a href="/" class="btn btn-primary">Start Scraping →</a>
                </div>
            </div>
        `;
    return;
  }

  articlesContainer.innerHTML = articles
    .map(
      (article) => `
            <div class="card" data-article-id="${article.id}">
                <div class="card-header">
                    <h3 class="card-title">${escapeHtml(article.title)}</h3>
                </div>
                <div class="card-body">
                    <div class="card-meta">
                        <div class="meta-item">
                            <span class="meta-label">Author:</span>
                            <span class="meta-value">${escapeHtml(article.author)}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Date:</span>
                            <span class="meta-value">${escapeHtml(formatDate(article.date))}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Website:</span>
                            <span class="meta-value">${escapeHtml(article.website_url)}</span>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <a href="${article.url}" target="_blank" class="card-link">
                        Read Article →
                    </a>
                </div>
            </div>
        `,
    )
    .join("");
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
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Format date string for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
  if (dateString === "N/A") return "N/A";
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
 * Search functionality
 */
searchInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  const filtered = articlesData.filter(
    (article) =>
      article.title.toLowerCase().includes(query) ||
      article.author.toLowerCase().includes(query),
  );
  renderArticles(filtered);
});

/**
 * Filter functionality
 */
filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    const filter = btn.dataset.filter;
    let filtered = articlesData;

    if (filter === "recent") {
      // Sort by date, most recent first
      filtered = [...articlesData].sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA;
      });
    } else if (filter === "today") {
      // Filter for today's articles
      const today = new Date().toISOString().split("T")[0];
      filtered = articlesData.filter((a) => a.date.startsWith(today));
    }

    renderArticles(filtered);
  });
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
    const response = await fetch("/api/clear-articles", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      articlesData = [];
      updateStats();
      renderArticles([]);
      alert("All articles have been deleted.");
    } else {
      showError("Failed to clear articles: " + data.message);
    }
  } catch (error) {
    console.error("Error clearing articles:", error);
    showError("Error clearing articles: " + error.message);
  }
});

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = "⚠️ " + message;
  document
    .querySelector(".container")
    .insertBefore(errorDiv, document.querySelector(".search-box"));
}
