from src.db.read_db import get_columns
import pandas as pd


def print_all_titles():
    rows = get_columns(["title"])
    for row in rows:
        print(row[0])


def print_tech(category: str = '', print_fn=print):
    rows = set(get_columns(['tech_stack','category'], where_clause=f"category LIKE '{category}'"))
    tech_tags = []
    for row in rows:
        tech_tags +=row[0].split(',')
    tech_tags = set(map(str.strip,tech_tags))
    print_fn(sorted(list(tech_tags)))

def get_stats():
    columns_query = ["title","category","salary_min_normalized","salary_max_normalized","years_of_experience_normalized"]
    
    rows = get_columns(columns_query)
    df = pd.DataFrame(rows, columns=columns_query)
    # filtered = df[(~df["salary_type"].str.contains('B2B H', na=False))]
    filtered = df[df["category"]=='Data'] # 'Fullstack', 'Frontend'
    filtered = filtered.drop(columns=["category"])

    filtered = filtered[(filtered["salary_min_normalized"].notna())] # (filtered["years_of_experience_normalized"].notna()) & 
    # filtered = filtered[(filtered["years_of_experience_normalized"] < 4 ) & (filtered["years_of_experience_normalized"] >= 0 )]
    print( filtered.sort_values(by='years_of_experience_normalized'))


def get_last_offers(number_of_offers: int = 10):
    rows = get_columns(["*"], limit=number_of_offers)
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    # df = get_stats()
    # print(df)
    print_tech(category='Data', print_fn=print)

    # df.to_csv('reports/last_offers.csv', index=False)
