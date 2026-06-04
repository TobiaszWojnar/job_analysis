import os
from bs4 import BeautifulSoup
from src.scraping.strategies.justjoinit_strategy import JustJoinItStrategy

def test():
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "offers", "Analityk_Analityczka Systemowo-Biznesowy_a - DCG.htm")
    print(f"Reading file: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    strategy = JustJoinItStrategy()
    
    print("Testing get_responsibilities via Ollama...")
    responsibilities = strategy.get_responsibilities(soup)
    
    print("\n--- EXTRACTED RESPONSIBILITIES ---")
    print(responsibilities)
    print("----------------------------------")

if __name__ == "__main__":
    test()
