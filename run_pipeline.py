#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import builtins
import psycopg2
from dotenv import load_dotenv
from src.db.init_db import create_database, create_table
from src.ollama import ensure_ollama_ready

# Force all print statements to flush immediately, preventing log buffering issues with subprocesses
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    builtins.print(*args, **kwargs)

load_dotenv()

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

def main():
    parser = argparse.ArgumentParser(
        description="Run Ollama, verify model presence, and process new job links.",
        add_help=False
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model to verify (default: {DEFAULT_MODEL})")
    
    # Parse only known args to allow forwarding everything else to process_new.py
    args, process_new_args = parser.parse_known_args()
    
    # Prepare environment with PYTHONPATH set to project root to allow imports under 'src'
    env = os.environ.copy()
    project_root = os.path.abspath(os.path.dirname(__file__))
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    # If the user passed -h or --help, print this script's help first, then process_new.py help
    if "-h" in process_new_args or "--help" in process_new_args:
        print("Usage: python run_pipeline.py [--model MODEL] [process_new.py arguments...]\n")
        print("Launcher Arguments:")
        print(f"  --model MODEL      Ollama model to verify (default: {DEFAULT_MODEL})")
        print("\nprocess_new.py Arguments:")
        # Try running process_new.py with --help to show its usage
        subprocess.run([sys.executable, os.path.join("src", "scraping", "process_new.py"), "--help"], env=env)
        sys.exit(0)

    # === STEP 1: Verify PostgreSQL Connection & Database Schema ===
    print("[Step 1/3] Verifying PostgreSQL connection and database schema...")
    try:
        # Create database and tables if they don't exist
        create_database()
        create_table()
        
        # Verify connection to the target database
        from src.db.modify_db import DB_CONFIG
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("  -> PostgreSQL connection and schema verified successfully.")
    except Exception as e:
        print(f"\nError: PostgreSQL verification failed: {e}", file=sys.stderr)
        print("Please make sure your PostgreSQL server is running and your .env configurations are correct.", file=sys.stderr)
        sys.exit(1)

    # === STEP 2: Verify Ollama & LLM Support ===
    print("\n[Step 2/3] Verifying LLM support (Ollama)...")
    try:
        ensure_ollama_ready(args.model)
        print("  -> Ollama LLM support verified successfully.")
    except Exception as e:
        print(f"\nError: Ollama LLM support verification failed: {e}", file=sys.stderr)
        sys.exit(1)

    # === STEP 3: Start Processing Job Links ===
    print("\n[Step 3/3] Starting job links scraping and processing...")
    cmd = [sys.executable, os.path.join("src", "scraping", "process_new.py")] + process_new_args
    try:
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running process_new.py: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
