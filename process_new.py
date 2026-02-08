import argparse
import sys
import time
import logging
from src.scraping.scrape_job import scrape_job_page
from src.links_cleaner import clean_links
from src.db.modify_db import save_to_postgres
from src.db.read_db import get_existing_links

def main():
    parser = argparse.ArgumentParser(description="Job Scraper")
    parser.add_argument("links_file", nargs="?", default="./links/new.txt", help="Path to the links file")
    args = parser.parse_args()

    # specific handler for errors
    error_handler = logging.FileHandler("logs/errors.log")
    error_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/scraper.log"),
            logging.StreamHandler(sys.stdout),
            error_handler
        ]
    )
    links_file = args.links_file

    try:
        with open(links_file, 'r') as f:
            urls = clean_links(f)
            
        existing_links = get_existing_links(urls)
        if existing_links:
            print(f"Skipping {len(existing_links)} links already in DB.")
            urls = [url for url in urls if url not in existing_links]
    except FileNotFoundError:
        print(f"Error: {links_file} not found.")
        return

    print(f"Found {len(urls)} URLs to process.")

    number_of_errors = 0
    for i, url in enumerate(urls, 1):
        logging.info(f"Processing ({i}/{len(urls)}): {url}")
        try:
            data = scrape_job_page(url)
            save_to_postgres(data)
            logging.info("  -> Saved successfully.")
        except Exception as e:
            logging.error(f"  -> Error processing {url}: {e}")
            number_of_errors += 1
        
        # Be nice to the server
        time.sleep(1)

    print("\n--- Final Report ---")
    print(f"Number of processed links: {len(urls)}")
    print(f"Number of saved links: {len(urls) - number_of_errors}")
    print(f"Number of errors: {number_of_errors}")

    # Clear the links file
    with open(links_file, 'w'):
        pass


if __name__ == "__main__":
    main()
