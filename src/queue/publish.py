#!/usr/bin/env python3
import os
import sys
import pika
from dotenv import load_dotenv

# Add project root to sys.path to support running this file directly from anywhere
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.links_cleaner import clean_links
from src.db.read_db import get_existing_links

def publish_once(links_file):
    # 1. Read and clean links from new.txt
    if not os.path.exists(links_file) or os.path.getsize(links_file) == 0:
        return False

    try:
        with open(links_file, "r", encoding="utf-8") as f:
            urls = clean_links(f)
    except Exception as e:
        print(f"Error reading links: {e}")
        return False

    if not urls:
        # Clear the file since it has no valid links
        try:
            with open(links_file, "w", encoding="utf-8"):
                pass
        except Exception as e:
            print(f"Error clearing empty links file: {e}")
        return True

    print(f"New links detected. Cleaned links. Total unique URLs: {len(urls)}")

    # 2. Filter out duplicates existing in PostgreSQL
    print("Checking PostgreSQL for already scraped job links...")
    try:
        existing_urls = get_existing_links(urls)
        new_urls = [url for url in urls if url not in existing_urls]
    except Exception as e:
        print(f"Error checking PostgreSQL database: {e}")
        return False

    duplicates_count = len(urls) - len(new_urls)
    if duplicates_count > 0:
        print(f"Found {duplicates_count} links that are already present in the database. Skipping them.")

    if not new_urls:
        print("No new links left to publish. Clearing new.txt.")
        # Clear the input file since all were duplicates
        try:
            with open(links_file, "w", encoding="utf-8"):
                pass
        except Exception as e:
            print(f"Error clearing links file: {e}")
        return True

    # 3. Publish to RabbitMQ
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "job_links")

    print(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")
    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=2
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        rabbitmq_dlq = os.getenv("RABBITMQ_DLQ", "job_links_failed")
        dlx_exchange = "job_links_dlx"
        channel.exchange_declare(exchange=dlx_exchange, exchange_type="direct")
        
        arguments = {
            "x-dead-letter-exchange": dlx_exchange,
            "x-dead-letter-routing-key": rabbitmq_dlq
        }
        # Declare the primary queue as durable with DLX arguments
        channel.queue_declare(queue=rabbitmq_queue, durable=True, arguments=arguments)

        print(f"Publishing {len(new_urls)} URLs to queue '{rabbitmq_queue}'...")
        published_count = 0
        for url in new_urls:
            channel.basic_publish(
                exchange="",
                routing_key=rabbitmq_queue,
                body=url,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent on disk
                )
            )
            published_count += 1

        print(f"Successfully published {published_count} messages to RabbitMQ.")
        
        # Clear new.txt on success
        with open(links_file, "w", encoding="utf-8"):
            pass
        print("Cleared new.txt successfully.")

        connection.close()
        return True

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
        print(f"Error publishing to RabbitMQ: {error_msg}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

def main():
    load_dotenv()

    import argparse
    parser = argparse.ArgumentParser(description="Publish links to RabbitMQ queue")
    parser.add_argument("--watch", "-w", action="store_true", help="Monitor the links file and publish new links as they are added")
    args = parser.parse_args()

    # Ensure Docker and RabbitMQ are running
    from src.queue.setup_rabbitmq import ensure_rabbitmq_ready
    ensure_rabbitmq_ready()

    # Paths
    links_file = os.path.join("links", "new.txt")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(links_file), exist_ok=True)
    if not os.path.exists(links_file):
        with open(links_file, "w", encoding="utf-8"):
            pass

    if args.watch:
        print(f"Publisher started in watch mode. Monitoring '{links_file}' for new links...")
        print("To exit press CTRL+C")
        import time
        try:
            while True:
                publish_once(links_file)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nPublisher watch stopped.")
            sys.exit(0)
    else:
        success = publish_once(links_file)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
