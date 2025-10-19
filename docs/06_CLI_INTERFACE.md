# CLI Interface Documentation

## Overview

The Tech Trends Database Scraper now features a comprehensive command-line interface (CLI) built with Python's `argparse` module. This allows users to control the scraper's behavior directly from the terminal without modifying code.

## Command Structure

```bash
python main.py --urls URL [URL ...] [--workers N] [--mode {normal|debug}]
```

## Arguments

### 1. `--urls` (Required)

**Purpose:** Specify one or more website URLs to scrape.

**Type:** String (accepts multiple values)

**Required:** Yes

**Syntax:**
```bash
python main.py --urls <URL> [<URL2> <URL3> ...]
```

**Examples:**
```bash
# Single URL
python main.py --urls https://realpython.com/

# Multiple URLs
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog
```

**Error Handling:**
If `--urls` is not provided, the program exits with an error:
```
main.py: error: the following arguments are required: --urls
```

---

### 2. `--workers` (Optional)

**Purpose:** Control the number of concurrent worker threads used for scraping.

**Type:** Integer

**Default:** 5

**Minimum Recommended:** 1

**Maximum Recommended:** 10 (depends on system resources)

**Syntax:**
```bash
python main.py --urls <URL> --workers <N>
```

**Examples:**
```bash
# Use 3 worker threads
python main.py --urls https://realpython.com/ --workers 3

# Use 10 worker threads for faster scraping (if system allows)
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news --workers 10

# Use default 5 workers
python main.py --urls https://realpython.com/
```

**Performance Notes:**
- **Fewer workers (1-3):** Lower resource usage, slower scraping
- **Default (5):** Balanced performance and resource usage
- **More workers (6-10):** Higher resource usage, potentially faster scraping
- **Too many workers:** May cause system overload or network throttling

**Error Handling:**
If a non-integer value is provided:
```
main.py: error: argument --workers: invalid int value: 'abc'
```

---

### 3. `--mode` (Optional)

**Purpose:** Control the verbosity and output level of the application.

**Type:** String (restricted to specific values)

**Default:** `normal`

**Allowed Values:** `normal` or `debug`

**Syntax:**
```bash
python main.py --urls <URL> --mode {normal|debug}
```

**Examples:**

**Normal Mode (Default):**
```bash
python main.py --urls https://realpython.com/ --mode normal
# or simply:
python main.py --urls https://realpython.com/
```

Output includes:
- Target websites
- Worker thread count
- Detailed results per website
- Aggregated statistics

**Debug Mode:**
```bash
python main.py --urls https://realpython.com/ --mode debug
```

Output includes:
- All normal mode output
- CLI configuration details
- 🔍 DEBUG MODE indicator
- Verbose logging information

**Error Handling:**
If an invalid mode is provided:
```
main.py: error: argument --mode: invalid choice: 'invalid' (choose from normal, debug)
```

---

## Usage Examples

### Basic Usage: Single URL with Defaults
```bash
python main.py --urls https://realpython.com/
```
- Uses 5 worker threads
- Output in normal mode
- Scrapes Real Python homepage

### Multiple URLs with Default Settings
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news
```
- Uses 5 worker threads
- Output in normal mode
- Scrapes 2 websites in parallel

### Custom Worker Count
```bash
python main.py --urls https://realpython.com/ --workers 3
```
- Uses 3 worker threads
- Output in normal mode
- Better for systems with limited resources

### All Three Arguments
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog --workers 3 --mode debug
```
- Scrapes 3 websites
- Uses 3 worker threads
- Shows debug information

### Debug Mode for Troubleshooting
```bash
python main.py --urls https://www.datacamp.com/blog --workers 2 --mode debug
```
- Scrapes DataCamp
- Uses 2 worker threads
- Shows verbose logging and configuration details

---

## Help Command

View all available arguments and examples:

```bash
python main.py --help
```

**Output:**
```
usage: main.py [-h] --urls URLS [URLS ...] [--workers WORKERS] [--mode {normal,debug}]

Tech Trends Database Scraper - Multi-Site Web Scraping Tool

options:
  -h, --help            show this help message and exit
  --urls URLS [URLS ...]
                        One or more full URLs of the websites you want to scrape.
  --workers WORKERS     Number of concurrent worker threads to use for scraping. (Default: 5)
  --mode {normal,debug}
                        Set the output mode. 'normal' for standard output, 'debug' for verbose logging. (Default: normal)

Examples:
  # Basic usage with required URLs argument
  python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news
  
  # Specify URLs, workers, and mode
  python main.py --urls https://www.datacamp.com/blog --workers 10 --mode debug
  
  # Use debug mode for verbose output
  python main.py --urls https://realpython.com/ --mode debug
```

---

## Output Format

### Normal Mode Output

```
======================================================================
Tech Trends Database Scraper - Multi-Site Collection
======================================================================

Target websites: 2
  1. https://realpython.com/
  2. https://www.freecodecamp.org/news

Worker threads: 5

======================================================================
DETAILED RESULTS BY WEBSITE
======================================================================

[OK] https://realpython.com/
   Created: 0 articles
   Skipped: 19 duplicates
   Errors: 0

[OK] https://www.freecodecamp.org/news
   Created: 0 articles
   Skipped: 25 duplicates

======================================================================
AGGREGATED STATISTICS
======================================================================

Total URLs Processed: 2
Successful: 2
Failed: 0

Total Articles:
  Created: 0
  Skipped (duplicates): 44
  Errors: 0
  Total Processed: 44

======================================================================
```

### Debug Mode Output

```
======================================================================
🔍 DEBUG MODE ENABLED - Verbose logging active
======================================================================

CLI Configuration:
  URLs to scrape: 2
  Worker threads: 5
  Output mode: debug

======================================================================
Tech Trends Database Scraper - Multi-Site Collection
======================================================================

Target websites: 2
  1. https://realpython.com/
  2. https://www.freecodecamp.org/news

Worker threads: 5

[... rest of normal output ...]
```

---

## Common Use Cases

### Use Case 1: Quick Scrape of Default Sites
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog
```

### Use Case 2: Fast Scraping with More Workers
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news --workers 8
```

### Use Case 3: Conservative Scraping on Limited Resources
```bash
python main.py --urls https://realpython.com/ --workers 2
```

### Use Case 4: Debugging Failed Scrapes
```bash
python main.py --urls https://www.datacamp.com/blog --mode debug
```

### Use Case 5: Full Multi-Site Scrape with Custom Configuration
```bash
python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news https://www.datacamp.com/blog --workers 4 --mode debug
```

---

## Error Handling and Troubleshooting

### Error: Missing `--urls` Argument
```
main.py: error: the following arguments are required: --urls
```
**Solution:** Provide at least one URL:
```bash
python main.py --urls https://realpython.com/
```

### Error: Invalid `--workers` Value
```
main.py: error: argument --workers: invalid int value: 'ten'
```
**Solution:** Use an integer value:
```bash
python main.py --urls https://realpython.com/ --workers 10
```

### Error: Invalid `--mode` Value
```
main.py: error: argument --mode: invalid choice: 'verbose' (choose from normal, debug)
```
**Solution:** Use `normal` or `debug`:
```bash
python main.py --urls https://realpython.com/ --mode debug
```

### Issue: Scraping Too Slow
**Solution:** Increase worker threads (if system resources allow):
```bash
python main.py --urls <URLs> --workers 8
```

### Issue: System Resource Overload
**Solution:** Decrease worker threads:
```bash
python main.py --urls <URLs> --workers 2
```

### Issue: Want More Information About What's Happening
**Solution:** Use debug mode:
```bash
python main.py --urls <URLs> --mode debug
```

---

## Technical Details

### Argument Parser Implementation

The CLI uses Python's `argparse` module with the following configuration:

- **Parser Type:** Standard ArgumentParser with RawDescriptionHelpFormatter
- **Required Arguments:** `--urls` (nargs='+')
- **Optional Arguments:** 
  - `--workers` (type=int, default=5)
  - `--mode` (choices=['normal', 'debug'], default='normal')

### Session Management

The CLI works seamlessly with the refactored session management:
- Single database session created for all worker threads
- Session shared across parallel processes
- Proper cleanup after scraping completes

### Thread Execution

- Arguments parsed once at startup
- Worker count passed to `run_many_and_aggregate()`
- All workers share a single database session
- Results aggregated after all threads complete

---

## Related Documentation

- [03_IMPLEMENTATION.md](03_IMPLEMENTATION.md) - Overall implementation details
- [04_TESTING.md](04_TESTING.md) - Testing procedures
- [05_STATUS.md](05_STATUS.md) - Current project status
- Main README.md - Quick start guide
