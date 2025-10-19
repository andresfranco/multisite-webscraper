"""Main entry point for the web scraper application."""
import sys
import argparse
from webscraper_core.manager import run_many_and_aggregate

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def main():
    """Scrape multiple tech education websites and aggregate statistics."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Tech Trends Database Scraper - Multi-Site Web Scraping Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage with required URLs argument
  python main.py --urls https://realpython.com/ https://www.freecodecamp.org/news
  
  # Specify URLs, workers, and mode
  python main.py --urls https://www.datacamp.com/blog --workers 10 --mode debug
  
  # Use debug mode for verbose output
  python main.py --urls https://realpython.com/ --mode debug
        '''
    )
    
    # Define required --urls argument
    parser.add_argument(
        '--urls',
        nargs='+',
        required=True,
        help='One or more full URLs of the websites you want to scrape.'
    )
    
    # Define optional --workers argument
    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of concurrent worker threads to use for scraping. (Default: 5)'
    )
    
    # Define optional --mode argument
    parser.add_argument(
        '--mode',
        choices=['normal', 'debug'],
        default='normal',
        help="Set the output mode. 'normal' for standard output, 'debug' for verbose logging. (Default: normal)"
    )
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Extract arguments
    urls = args.urls
    max_workers = args.workers
    mode = args.mode
    
    # Display debug mode indicator if enabled
    if mode == 'debug':
        print("=" * 70)
        print("🔍 DEBUG MODE ENABLED - Verbose logging active")
        print("=" * 70)
        print(f"\nCLI Configuration:")
        print(f"  URLs to scrape: {len(urls)}")
        print(f"  Worker threads: {max_workers}")
        print(f"  Output mode: {mode}")
        print("\n")
    
    print("=" * 70)
    print("Tech Trends Database Scraper - Multi-Site Collection")
    print("=" * 70)
    print(f"\nTarget websites: {len(urls)}")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    print(f"\nWorker threads: {max_workers}")
    print("\n")
    
    # Run scraper on all URLs and get aggregated results
    results, aggregated = run_many_and_aggregate(urls, max_workers=max_workers)
    
    # Display detailed results per URL
    print("\n" + "=" * 70)
    print("DETAILED RESULTS BY WEBSITE")
    print("=" * 70)
    
    for result in results:
        status_icon = "[OK]" if result.get('status') == 'success' else "[FAIL]"
        print(f"\n{status_icon} {result['url']}")
        print(f"   Created: {result.get('created', 0)} articles")
        print(f"   Skipped: {result.get('skipped', 0)} duplicates")
        if result.get('errors', 0) > 0:
            print(f"   Errors:  {result.get('errors', 0)}")
    
    # Display aggregated statistics
    print("\n" + "=" * 70)
    print("AGGREGATED STATISTICS")
    print("=" * 70)
    print(f"\nTotal URLs Processed: {aggregated.get('total_urls', 0)}")
    print(f"Successful: {aggregated.get('successful_urls', 0)}")
    print(f"Failed: {aggregated.get('failed_urls', 0)}")
    print(f"\nTotal Articles:")
    print(f"  Created: {aggregated.get('total_created', 0)}")
    print(f"  Skipped (duplicates): {aggregated.get('total_skipped', 0)}")
    print(f"  Errors: {aggregated.get('total_errors', 0)}")
    print(f"  Total Processed: {aggregated.get('total_created', 0) + aggregated.get('total_skipped', 0)}")
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()
