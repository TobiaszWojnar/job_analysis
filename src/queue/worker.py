#!/usr/bin/env python3
import os
import sys
import pika
import logging
import time
from dotenv import load_dotenv

# Add project root to sys.path to support running this file directly from anywhere
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scraping.scrape_job import scrape_job_page
from src.db.modify_db import save_to_postgres
from src.db.read_db import get_existing_links

def main():
    load_dotenv()

    # Parse arguments for worker ID
    import argparse
    parser = argparse.ArgumentParser(description="RabbitMQ Job Consumer Worker")
    parser.add_argument("--id", type=int, default=None, help="Optional worker ID for logging")
    args = parser.parse_args()

    worker_prefix = f"Worker {args.id} " if args.id is not None else "Worker "

    # Ensure Docker and RabbitMQ are running
    from src.queue.setup_rabbitmq import ensure_rabbitmq_ready
    ensure_rabbitmq_ready()

    # Configure logging
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Specific error handler file logging
    error_handler = logging.FileHandler(os.path.join(log_dir, "worker_errors.log"))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(f'%(asctime)s - %(levelname)s - {worker_prefix}%(message)s'))

    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - %(levelname)s - {worker_prefix}%(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "worker.log")),
            logging.StreamHandler(sys.stdout),
            error_handler
        ]
    )

    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    rabbitmq_queue = os.getenv("RABBITMQ_QUEUE", "job_links")
    rabbitmq_dlq = os.getenv("RABBITMQ_DLQ", "job_links_failed")

    logging.info(f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")
    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        max_retries = 5
        retry_delay = 5
        connection = None
        for attempt in range(1, max_retries + 1):
            try:
                connection = pika.BlockingConnection(parameters)
                break
            except Exception as e:
                if attempt == max_retries:
                    raise
                logging.warning(f"Connection attempt {attempt}/{max_retries} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)

        channel = connection.channel()

        # 1. Declare the Dead-Letter Exchange (DLX)
        dlx_exchange = "job_links_dlx"
        channel.exchange_declare(exchange=dlx_exchange, exchange_type="direct")

        # 2. Declare the Dead-Letter Queue (DLQ) as durable
        channel.queue_declare(queue=rabbitmq_dlq, durable=True)
        channel.queue_bind(exchange=dlx_exchange, queue=rabbitmq_dlq, routing_key=rabbitmq_dlq)

        # 3. Declare the main queue with arguments pointing to the DLX
        arguments = {
            "x-dead-letter-exchange": dlx_exchange,
            "x-dead-letter-routing-key": rabbitmq_dlq
        }
        channel.queue_declare(queue=rabbitmq_queue, durable=True, arguments=arguments)

        # 4. Set Quality of Service (prefetch=1) for fair dispatch among concurrent workers
        channel.basic_qos(prefetch_count=1)

        logging.info(f"Worker daemon started. Listening for messages on '{rabbitmq_queue}'...")
        logging.info("To exit press CTRL+C")

        was_empty = False
        while True:
            # Process any network/event loop callbacks (needed for keepalives)
            connection.process_data_events()
            
            method_frame, header_frame, body = channel.basic_get(queue=rabbitmq_queue)
            if method_frame:
                was_empty = False
                url = body.decode("utf-8").strip()
                remaining = method_frame.message_count
                remaining_str = f"{remaining} remaining in queue" if remaining is not None else "unknown count remaining"
                logging.info(f"Worker took URL from queue: {url} ({remaining_str})")
                
                # Double check database to prevent duplicate scraping (Race Condition prevention)
                try:
                    if get_existing_links([url]):
                        logging.info(f"  -> Link already exists in DB. Skipping scraping: {url}")
                        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                        logging.info(f"Worker finished processing: {url}")
                        continue
                except Exception as e:
                    logging.error(f"  -> Error checking DB for duplicates for URL {url}: {e}")
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
                    continue

                # Process the job scraping and saving
                try:
                    data = scrape_job_page(url)
                    save_to_postgres(data)
                    logging.info("  -> Successfully processed and saved to DB.")
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    logging.info(f"Worker finished processing: {url}")
                except Exception as e:
                    logging.error(f"  -> Error processing URL {url}: {e}")
                    logging.info("  -> Routing URL to Dead-Letter Queue (DLQ) for manual review.")
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
                    logging.info(f"Worker finished processing (with error): {url}")
            else:
                if not was_empty:
                    logging.info("Worker has nothing to take from queue. Waiting for new messages...")
                    was_empty = True
                time.sleep(2)

    except KeyboardInterrupt:
        logging.info("Shutting down worker daemon...")
        try:
            connection.close()
        except NameError:
            pass
        logging.info("Worker daemon stopped.")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Fatal worker exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
