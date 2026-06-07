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
from src.queue.setup_rabbitmq import ensure_rabbitmq_ready

# Force all print statements to flush immediately, preventing log buffering issues with subprocesses
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    builtins.print(*args, **kwargs)

load_dotenv()

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

def main():
    parser = argparse.ArgumentParser(
        description="Run RabbitMQ publisher and consumer workers, verifying database and Ollama setup."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model to verify (default: {DEFAULT_MODEL})")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel worker processes to start (default: 1). Only use if you want more than one worker.")
    
    args = parser.parse_args()
    
    # Prepare environment with PYTHONPATH set to project root to allow imports under 'src'
    env = os.environ.copy()
    project_root = os.path.abspath(os.path.dirname(__file__))
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    total_steps = 5

    # === STEP 1: Verify PostgreSQL Connection & Database Schema ===
    print(f"[Step 1/{total_steps}] Verifying PostgreSQL connection and database schema...")
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
    print(f"\n[Step 2/{total_steps}] Verifying LLM support (Ollama)...")
    try:
        ensure_ollama_ready(args.model)
        print("  -> Ollama LLM support verified successfully.")
    except Exception as e:
        print(f"\nError: Ollama LLM support verification failed: {e}", file=sys.stderr)
        sys.exit(1)

    # === STEP 3: Verify RabbitMQ & Docker Support ===
    print(f"\n[Step 3/{total_steps}] Verifying RabbitMQ support (Docker)...")
    try:
        ensure_rabbitmq_ready()
        print("  -> RabbitMQ support verified successfully.")
    except Exception as e:
        print(f"\nError: RabbitMQ support verification failed: {e}", file=sys.stderr)
        sys.exit(1)

    # === STEP 4: Publish Links ===
    print(f"\n[Step 4/{total_steps}] Publishing links from new.txt to RabbitMQ...")
    cmd_publish = [sys.executable, os.path.join("src", "queue", "publish.py")]
    try:
        result = subprocess.run(cmd_publish, env=env)
        if result.returncode != 0:
            print(f"\nError: Publishing links failed with return code {result.returncode}.", file=sys.stderr)
            sys.exit(result.returncode)
    except Exception as e:
        print(f"\nError running publisher: {e}", file=sys.stderr)
        sys.exit(1)

    # === STEP 5: Start Consumer Workers ===
    workers_count = args.workers
    if workers_count > 1:
        print(f"\n[Step 5/{total_steps}] Starting {workers_count} parallel consumer workers...")
        processes = []
        for i in range(workers_count):
            p = subprocess.Popen(
                [sys.executable, os.path.join("src", "queue", "worker.py"), "--id", str(i + 1)],
                env=env
            )
            processes.append(p)
        print(f"  -> Successfully started {workers_count} parallel background workers.")
        try:
            # Block and wait for all workers
            for p in processes:
                p.wait()
        except KeyboardInterrupt:
            print("\nShutting down all workers...")
            for p in processes:
                p.terminate()
            for p in processes:
                p.wait()
            print("All workers stopped.")
            sys.exit(0)
    else:
        print(f"\n[Step 5/{total_steps}] Starting a single consumer worker...")
        cmd_worker = [sys.executable, os.path.join("src", "queue", "worker.py"), "--id", "1"]
        try:
            result = subprocess.run(cmd_worker, env=env)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            print("\nWorker stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
