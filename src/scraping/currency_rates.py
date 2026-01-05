import sys
import requests
import cloudscraper
import datetime

def scrape_currency_rates(url: str) -> dict:
    try:
        session = cloudscraper.create_scraper()
    except ImportError:
        session = requests.Session()

    response = session.get(url)
    
    if response.status_code == 403:
        raise RuntimeError(
            "403 Forbidden – site likely uses Cloudflare. "
            "Install cloudscraper: pip install cloudscraper"
        )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":

    start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    currency = "usd"

    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}/?format=json"

    try:
        rates = scrape_currency_rates(url).get("rates")
        if rates:
             average_mid = sum(rate['mid'] for rate in rates) / len(rates)
             print(f"{average_mid:.2f}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
