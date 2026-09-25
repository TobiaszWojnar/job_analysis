# Implementation Plan: Network Loss Resilience, Error Link Logging & DLQ Requeue Utility

Fix worker handling during internet loss by implementing a **Pause & Retry** mechanism for network failures, separate logging for failed links to `error_links.log`, and creating a `requeue_dlq.py` script to manage and retry messages stuck in the Dead-Letter Queue (DLQ).

## Proposed Changes

### Queue Workers & Scraper Utils

#### [NEW] [network_utils.py](file:///c:/Users/wojna/Code,%20Data,%20Study/code/job_analysis/src/utils/network_utils.py)
- Create helper functions to detect transient network/connectivity exceptions (`is_network_error(exc)`) including:
  - `requests.exceptions.ConnectionError`, `Timeout`, `SSLError`
  - `urllib3.exceptions.NameResolutionError`, `MaxRetryError`
  - `socket.gaierror`, `OSError` (e.g. `[Errno 11001]`, `[WinError 10053]`)
- Add a connectivity check function `check_internet_connection()` to test if internet connectivity has been restored before retrying scraping.

---

#### [MODIFY] [worker.py](file:///c:/Users/wojna/Code,%20Data,%20Study/code/job_analysis/src/queue/worker.py)
- **Error Link Logger**: Configure a dedicated file logger pointing to `logs/error_links.log` that formats failed URLs along with a short error message (`TIMESTAMP | URL | Error: <reason>`).
- **Pause & Retry Logic for Internet Loss**:
  - Catch exceptions during `scrape_job_page(url)`.
  - If `is_network_error(e)` is true:
    - Log a warning: `Worker X lost internet connectivity while processing <url>. Pausing worker...`
    - Enter a pause & retry loop with exponential backoff (e.g., 10s, 20s, 30s up to a cap).
    - Call `connection.process_data_events()` during sleep to keep the RabbitMQ heartbeat active.
    - If connection drops, attempt RabbitMQ connection recovery before retrying the job.
    - Once internet is back, retry scraping the URL without routing it to DLQ.
- **Non-Network Errors & DLQ Routing**:
  - For non-network failures (e.g. HTTP 404, parsing error) or if network retries exceed max limit:
    - Write to `logs/worker_errors.log`.
    - Write to `logs/error_links.log`.
    - Nack message with `requeue=False` to route URL to the DLQ (`job_links_failed`).

---

#### [NEW] [requeue_dlq.py](file:///c:/Users/wojna/Code,%20Data,%20Study/code/job_analysis/src/queue/requeue_dlq.py)
- Create a script to inspect and requeue messages from the DLQ (`job_links_failed`) back to the main queue (`job_links`).
- Features:
  - Move all or N messages from DLQ back to `job_links`.
  - Print current count of messages in `job_links` and `job_links_failed`.
  - Support arguments `--count` and `--all`.

---

## Verification Plan

### Automated / Script Verification
- Test network exception detection logic against mock network errors.
- Test `requeue_dlq.py` script against RabbitMQ (or local Docker container).

### Manual Verification
1. Run `python -m src.queue.worker --id 1` in a test run.
2. Verify that `logs/error_links.log` correctly logs failed links with short descriptions.
3. Test network outage simulation by temporarily pointing request or blocking connection, verifying worker enters pause & retry loop and resumes when connection is restored.
4. Verify `python -m src.queue.requeue_dlq --all` successfully moves DLQ messages back to `job_links`.
