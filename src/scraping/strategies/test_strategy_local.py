import os
from bs4 import BeautifulSoup
from justjoinit_strategy import JustJoinItStrategy

def test_file(file_path, output_file, strategy):
    output_file.write(f"\nTesting file: {file_path}\n")
    if not os.path.exists(file_path):
        output_file.write("File not found.\n")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    output_file.write(f"Title: {strategy.get_title(soup)}\n")
    output_file.write(f"Company: {strategy.get_company(soup)}\n")
    output_file.write(f"Company Link: {strategy.get_company_link(soup)}\n")
    output_file.write(f"Category: {strategy.get_category(soup)}\n")
    output_file.write(f"Tech Stack: {strategy.get_tech_stack(soup)}\n")
    output_file.write(f"Location: {strategy.get_location(soup)}\n")
    output_file.write(f"Location Type: {strategy.get_location_type(soup)}\n")
    output_file.write(f"Salary: {strategy.get_salary(soup)}\n")
    output_file.write(f"Salary Type: {strategy.get_salary_type(soup)}\n")
    output_file.write(f"Exp: {strategy.get_years_of_experience(soup)}\n")
    # print(f"Responsibilities: {strategy.get_responsibilities(soup)[:100]}...")
    # print(f"Requirements: {strategy.get_requirements(soup)[:100]}...")

if __name__ == "__main__":
    links_dir = "links" # TODO update path
    strategy = JustJoinItStrategy() # TODO configure strategy

    
    with open("logs/verification_results.txt", "w", encoding="utf-8") as out:
        for filename in os.listdir(links_dir):
            if filename.endswith(".htm"):
                try:
                    test_file(os.path.join(links_dir, filename), out, strategy)
                except Exception as e:
                    out.write(f"Error testing {filename}: {e}\n")
