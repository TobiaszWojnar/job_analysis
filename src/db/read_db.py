import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_existing_links(links):
    if not links:
        return list()
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Use ANY for cleaner array handling
    cur.execute("SELECT link FROM job_offers WHERE link = ANY(%s)", (links,))
    existing = {row[0] for row in cur.fetchall()}
    
    cur.close()
    conn.close()
    return existing

def get_similar_links(links):
    if not links:
        return set()
    # https://nofluffjobs.com/pl/job/ai-engineer-addepto-remote-20
    # https://nofluffjobs.com/pl/job/ai-engineer-addepto-remote-scalp8lg

    # https://www.pracuj.pl/praca/net-developer-katowice,oferta,1004426180
    # https://www.pracuj.pl/praca/net-developer-katowice,oferta,1004429183

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Use ANY for cleaner array handling
    cur.execute("SELECT link FROM job_offers WHERE link = ANY(%s)", (links,)) #TODO LIKE '{old_prefix}%'
    existing = {row[0] for row in cur.fetchall()}
    
    cur.close()
    conn.close()
    return existing

def get_columns(column_list: list[str]):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT " + ", ".join(column_list) + " FROM job_offers")
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows
    
def main():
    for row in set(get_columns(['salary'])):
        print(row[0])
    print("##---Done---##")

if __name__ == "__main__":
    main()