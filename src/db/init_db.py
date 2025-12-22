import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
# You can set these via environment variables or edit them here
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to default 'postgres' database to create a new db
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()

        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def create_table():
    """Create the job_offers table in the target database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        cur = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS job_offers (
            id SERIAL PRIMARY KEY,
            category VARCHAR(255),
            tech_stack TEXT,
            comment TEXT,
            status VARCHAR(50),
            sent_date DATE,
            response_date DATE,
            link TEXT UNIQUE,
            title VARCHAR(255),
            location VARCHAR(255),
            location_type VARCHAR(50),
            salary TEXT,
            salary_type VARCHAR(50),
            years_of_experience TEXT,
            company VARCHAR(255),
            company_link VARCHAR(255),
            company_description TEXT,
            responsibilities TEXT,
            requirements TEXT,
            benefits TEXT,
            body TEXT,
            full_offer TEXT,
            date_of_access DATE
        );
        """

        print(f"Creating table 'job_offers' in '{DB_NAME}'...")
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'job_offers' created/verified successfully.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_database()
    create_table()
