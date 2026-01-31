import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from typing import Callable, Any
import re
import logging

logger = logging.getLogger(__name__)

from ..utils.salary_utils import (
    calculate_min_max,
    calculate_years_normalized,
)

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
            data.get('date_of_access'),
            data.get('salary_min_normalized'),
            data.get('salary_max_normalized'),
            data.get('years_of_experience_normalized')
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
        
def normalize_salary() -> None:
    """Normalize salary columns using the generic update function."""
    columns = ['id', 'salary', 'salary_type', 'full_offer', 'salary_min_normalized', 'salary_max_normalized']
    where_min = "salary_min_normalized is null and salary not like ''"
    where_max = "salary_max_normalized is null and salary not like ''"
    
    def transform_min(row: tuple) -> int | None:
        _, salary, salary_type, full_offer, salary_min, salary_max = row
        if salary_min and salary_max:
            return None
        if salary is None or salary == '':
            return None
        min_value, _ = calculate_min_max(salary, salary_type, full_offer)
        return min_value
    
    def transform_max(row: tuple) -> int | None:
        _, salary, salary_type, full_offer, salary_min, salary_max = row
        if salary_min and salary_max:
            return None
        if salary is None or salary == '':
            return None
        _, max_value = calculate_min_max(salary, salary_type, full_offer)
        return max_value
    
    update_rows_with_function(
        columns_to_fetch=columns,
        column_to_update='salary_min_normalized',
        transform_func=transform_min,
        where_clause=where_min
    )
    
    update_rows_with_function(
        columns_to_fetch=columns,
        column_to_update='salary_max_normalized',
        transform_func=transform_max,
        where_clause=where_max
    )

def update_rows_with_function(
    columns_to_fetch: list[str],
    column_to_update: str,
    transform_func: Callable[[tuple], Any],
    where_clause: str = ""
) -> None:
    """Generic function to update a column based on values from other columns.
    
    Args:
        columns_to_fetch: List of column names to fetch (first should be 'id')
        column_to_update: Name of the column to update
        transform_func: Function that takes a tuple of fetched values and returns the new value.
                       Should return None to skip updating that row.
        where_clause: Optional WHERE clause (without 'WHERE' keyword) to filter rows
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Build SELECT query
        columns_sql = sql.SQL(", ").join(sql.Identifier(col) for col in columns_to_fetch)
        select_query = sql.SQL("SELECT {} FROM job_offers").format(columns_sql)
        
        if where_clause:
            select_query = sql.SQL("{} WHERE {}").format(select_query, sql.SQL(where_clause))
        
        update_query = sql.SQL("UPDATE job_offers SET {} = %s WHERE id = %s").format(
            sql.Identifier(column_to_update)
        )

        cur.execute(select_query)
        rows = cur.fetchall()
        
        total_rows = len(rows)
        skipped_rows = 0
        updated_rows = 0

        for row in rows:
            row_id = row[0]  # First column should be 'id'
            
            new_value = transform_func(row)

            if new_value is None:
                skipped_rows += 1
                continue

            cur.execute(update_query, (new_value, row_id))
            updated_rows += 1
        
        conn.commit()
        
        logger.info(f"update_rows_with_function({column_to_update}): "
                   f"matched={total_rows}, updated={updated_rows}, skipped={skipped_rows}")
    except Exception as e:
        logger.error(f"An error occurred updating {column_to_update}: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def normalize_years_of_experience() -> None:
    """Normalize years of experience column using the generic update function."""
    def transform(row: tuple) -> int | None:
        _, years_of_experience, years_of_experience_normalized = row
        if years_of_experience_normalized is not None:
            return None  # Skip if already normalized
        return calculate_years_normalized(years_of_experience)
    
    update_rows_with_function(
        columns_to_fetch=['id', 'years_of_experience', 'years_of_experience_normalized'],
        column_to_update='years_of_experience_normalized',
        transform_func=transform,
        where_clause="years_of_experience not like '' and years_of_experience_normalized is null"
    )

def main():
    # removeprefix_column('company_description', 'O firmie')
    # removeprefix_column('benefits', 'Udogodnienia w biurze')
    # add_prefix_column('company_link', '/praca?', 'https://theprotocol.it/praca?')
    update_column_with_function('salary', lambda x:re.sub(r'(?<=\d)[ \u00A0](?=\d)', '', x) if x else x)
    print("Done")

if __name__ == "__main__":
    main()
