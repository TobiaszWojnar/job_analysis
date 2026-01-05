from src.db.read_db import get_columns
import pandas as pd


def print_all_titles():
    rows = get_columns(["title"])
    for row in rows:
        print(row[0])


def print_tech(category: str = ''):
    rows = set(get_columns(['tech_stack','category'], where_clause=f"category LIKE '{category}'"))
    tech_tags = []
    for row in rows:
        tech_tags +=row[0].split(',')
    tech_tags = set(map(str.strip,tech_tags))
    print(sorted(list(tech_tags)))

def get_stats():
    rows = get_columns(["salary_type","category","salary","years_of_experience"])
    df = pd.DataFrame(rows, columns=["salary_type","category","salary","years_of_experience"])
    filtered = df[(~df["salary_type"].str.contains('B2B H', na=False))]
    filtered = filtered[(filtered["years_of_experience"].notna()) & (filtered["salary"] != '')]
    print( filtered[filtered["category"]=='Fullstack'].sort_values(by='years_of_experience'))


def get_last_offers(number_of_offers: int = 10):
    rows = get_columns(["*"], limit=number_of_offers)
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = get_last_offers(8)
    print(df)

    df.to_csv('reports/last_offers.csv', index=False)
