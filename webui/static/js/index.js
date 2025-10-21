// ===================================
// Index Page JavaScript
// ===================================

const form = document.getElementById('scraperForm');
const scrapeBtn = document.getElementById('scrapeBtn');
const clearBtn = document.getElementById('clearBtn');
const statusDiv = document.getElementById('status');
const customUrlInput = document.getElementById('customUrl');
const urlError = document.getElementById('urlError');

/**
 * Handle form submission for scraping
 */
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    urlError.textContent = '';

    // Get selected URLs
    const checkboxes = document.querySelectorAll('input[name="urls"]:checked');
    let urls = Array.from(checkboxes).map(cb => cb.value);

    // Add custom URLs
    const customUrls = customUrlInput.value
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);

    urls = [...urls, ...customUrls];

    if (urls.length === 0) {
        showStatus('Please select at least one URL', 'error');
        return;
    }

    // Validate custom URLs
    for (let url of customUrls) {
        if (!isValidUrl(url)) {
            urlError.textContent = `Invalid URL: ${url}`;
            showStatus('Invalid URL format detected', 'error');
            return;
        }
    }

    scrapeBtn.disabled = true;
    clearBtn.disabled = true;

    try {
        showStatus('🔄 Scraping in progress...', 'loading');

        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: urls,
                workers: parseInt(document.getElementById('workers').value)
            })
        });

        const data = await response.json();

        if (data.success) {
            let message = `✅ Scraping completed!\n`;
            message += `Created: ${data.stats.total_created} articles\n`;
            message += `Skipped: ${data.stats.total_skipped} (duplicates)\n`;
            message += `Errors: ${data.stats.total_errors}`;

            showStatus(message, 'success');
            customUrlInput.value = '';

            // Show stats
            if (data.stats) {
                let statsHtml = '<div class="stats">';
                statsHtml += `<div class="stat-item"><div class="stat-label">URLs Processed</div><div class="stat-value">${data.stats.successful_urls}</div></div>`;
                statsHtml += `<div class="stat-item"><div class="stat-label">Articles Created</div><div class="stat-value">${data.stats.total_created}</div></div>`;
                statsHtml += `<div class="stat-item"><div class="stat-label">Duplicates</div><div class="stat-value">${data.stats.total_skipped}</div></div>`;
                statsHtml += `<div class="stat-item"><div class="stat-label">Errors</div><div class="stat-value">${data.stats.total_errors}</div></div>`;
                statsHtml += '</div>';
                statusDiv.innerHTML += statsHtml;
            }
        } else {
            showStatus(`❌ Error: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        scrapeBtn.disabled = false;
        clearBtn.disabled = false;
    }
});

/**
 * Handle clear button click
 */
clearBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to delete all articles?')) {
        return;
    }

    scrapeBtn.disabled = true;
    clearBtn.disabled = true;

    try {
        showStatus('🔄 Clearing articles...', 'loading');

        const response = await fetch('/api/clear-articles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showStatus(`✅ ${data.message}`, 'success');
        } else {
            showStatus(`❌ Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        scrapeBtn.disabled = false;
        clearBtn.disabled = false;
    }
});

/**
 * Display status message
 * @param {string} message - Message to display
 * @param {string} type - Type of message (success, error, loading)
 */
function showStatus(message, type) {
    statusDiv.textContent = '';
    statusDiv.className = `status show ${type}`;

    if (type === 'loading') {
        statusDiv.innerHTML = `<span class="spinner"></span>${message}`;
    } else {
        statusDiv.innerHTML = message.replace(/\n/g, '<br>');
    }
}

/**
 * Validate URL format
 * @param {string} string - URL string to validate
 * @returns {boolean} True if valid URL, false otherwise
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}
