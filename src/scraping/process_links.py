import sys
import os

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from scraping.scrape_job import scrape_job_page, get_strategy

def process_links(file_path: str, process_result_function):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    print(f"Found {len(links)} links. Starting scraping...")

    for i, url in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Scraping: {url}")
        try:
            strategy = get_strategy(url)
            data = scrape_job_page(url, strategy)
            # Create a copy for printing to avoid modifying the original data if needed elsewhere
            data_to_print = {k: v for k, v in data.items() if k not in ['body', 'full_offer']}
            print(f"Success: {data_to_print}")
            process_result_function(data)

            # Here we could save the data, but for now we just print as requested
            print("-" * 50)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_links_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    process_links(file_path,print)
