import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import cloudscraper

from src.scraping.strategies.base_strategy import BaseJobStrategy
from src.scraping.strategies.pracuj_strategy import PracujStrategy
from src.scraping.strategies.nofluff_strategy import NoFluffStrategy
from src.scraping.strategies.protocol_strategy import ProtocolStrategy

# from strategies.base_strategy import BaseJobStrategy
# from strategies.pracuj_strategy import PracujStrategy
# from strategies.nofluff_strategy import NoFluffStrategy
# from strategies.protocol_strategy import ProtocolStrategy



def scrape_job_page(url: str) -> dict:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    try:
        strategy = get_strategy(url)
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        response = scraper.get(url, headers=HEADERS)

    except ImportError:
        response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 403:
        raise Exception("403 Forbidden: The site is blocking the request. Please install 'cloudscraper' to bypass this: pip install cloudscraper")
        
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return {
        'date_of_access': datetime.now().strftime('%Y-%m-%d'),
        'link': url,
        'body': response.text,
        'title': strategy.get_title(soup),
        'company': strategy.get_company(soup),
        'company_link': strategy.get_company_link(soup),
        'company_description': strategy.get_company_description(soup),
        'category': strategy.get_category(soup),
        'tech_stack': strategy.get_tech_stack(soup),
        'location': strategy.get_location(soup),
        'location_type': strategy.get_location_type(soup),
        'salary': strategy.get_salary(soup),
        'salary_type': strategy.get_salary_type(soup),
        'years_of_experience': strategy.get_years_of_experience(soup),
        'responsibilities': strategy.get_responsibilities(soup),
        'requirements': strategy.get_requirements(soup),
        'benefits': strategy.get_benefits(soup),
        'full_offer': strategy.get_full_offer(soup),
    }

def get_strategy(url: str) -> BaseJobStrategy:
    if "pracuj.pl" in url:
        return PracujStrategy()
    if "nofluffjobs.com" in url:
        return NoFluffStrategy()
    if "theprotocol.it" in url:
        return ProtocolStrategy()
    
    # Default fallback or raise error
    raise ValueError(f"No strategy found for URL: {url}")

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print(f"Usage: python {sys.argv[0]} <url>")
    #     sys.exit(1)
    # url = sys.argv[1]

    url = "https://www.pracuj.pl/praca/analityk-biznesowy-katowice,oferta,1004548049"

    try:
        result = scrape_job_page(url)
        data_to_print = {k: v for k, v in result.items() if k not in ['body', 'full_offer']}
        print(f"Success: {data_to_print}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
