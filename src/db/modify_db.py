import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from typing import Callable, Any
import re

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def save_to_postgres(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute(
        sql.SQL("""
            INSERT INTO job_offers (
                category, tech_stack, comment, status, sent_date, response_date, 
                link, title, location, location_type, salary, salary_type, 
                years_of_experience, company, company_link, company_description, 
                responsibilities, requirements, benefits, 
                body, full_offer, date_of_access
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, 
                %s, %s, %s, %s, 
                %s, %s
            )
        """),
        (
            data.get('category'),
            data.get('tech_stack'),
            data.get('comment'),
            data.get('status'),
            data.get('sent_date'),
            data.get('response_date'),
            data.get('link'),
            data.get('title'),
            data.get('location'),
            data.get('location_type'),
            data.get('salary'),
            data.get('salary_type'),
            data.get('years_of_experience'),
            data.get('company'),
            data.get('company_link'),
            data.get('company_description'),
            data.get('responsibilities'),
            data.get('requirements'),
            data.get('benefits'),
            data.get('body'),
            data.get('full_offer'),
            data.get('date_of_access')
        )
    )
    conn.commit()
    cur.close()
    conn.close()

def removeprefix_column(column_name: str, prefix: str) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute(f"UPDATE job_offers SET {column_name} = CASE WHEN {column_name} LIKE '{prefix} %' THEN substring({column_name} FROM length('{prefix} ') + 1) ELSE {column_name} END;")
    conn.commit()
    
    cur.close()
    conn.close()

def add_prefix_column(column_name: str, old_prefix: str, new_prefix: str) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    # https://theprotocol.it/praca?kw=people+more+p.s.a.
    # /praca?kw=people+more+p.s.a.

    cur.execute(f"UPDATE job_offers SET {column_name} = CASE WHEN {column_name} LIKE '{old_prefix}%' THEN '{new_prefix}' || substring({column_name} FROM length('{old_prefix} ') + 1) ELSE {column_name} END;")
    conn.commit()
    
    cur.close()
    conn.close()



def update_column_with_function(column_name: str, func: Callable[[Any], Any]) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Select all ids and the specific column
        # using sql.SQL to safely handle column names
        select_query = sql.SQL("SELECT id, {} FROM job_offers").format(sql.Identifier(column_name))
        cur.execute(select_query)
        rows = cur.fetchall()

        for row_id, value in rows:
            new_value = func(value)
            
            # Update the column with the new value
            update_query = sql.SQL("UPDATE job_offers SET {} = %s WHERE id = %s").format(sql.Identifier(column_name))
            cur.execute(update_query, (new_value, row_id))
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()



def main():
    # removeprefix_column('company_description', 'O firmie')
    # removeprefix_column('benefits', 'Udogodnienia w biurze')
    # add_prefix_column('company_link', '/praca?', 'https://theprotocol.it/praca?')
    update_column_with_function('salary', lambda x:re.sub(r'(?<=\d)[ \u00A0](?=\d)', '', x) if x else x)
    print("Done")

if __name__ == "__main__":
    main()
