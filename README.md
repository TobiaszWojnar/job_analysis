# Job Search Data Pipeline

## Overview
This project is designed to help you collect, clean, analyze, and report on job listings over time. The goal is to compile detailed statistics such as average salary for given years of experience, technology stack, and more, to support your job search and market research.

### Project Vision
1. **Link Collection**: Post lists of job offer links to the system.
2. **Cleaner Module**: Removes duplicates and unnecessary URL parameters.
3. **Queue System**: Cleaned links are published to a queue for asynchronous processing.
4. **Scraper Module**: Consumes links from the queue, scrapes job pages, and extracts fields like years of experience, salary, tech stack, benefits, and location.
5. **Database Storage**: Extracted data is saved to a database for further analysis.
6. **Reporting Module**: Generates reports such as average salary per technology stack, word clouds for job types, and various graphs.

### Architecture Diagram
```mermaid
flowchart TD
    A[User posts list of links] --> B[Cleaner Module]
    B --> C[Queue]
    C --> D[Scraper Module]
    D --> E[Database]
    E --> F[Reporting Module]
```

## Database Schema
The following fields are stored in the database for each job listing:

| Field | Type | Description |
| :--- | :--- | :--- |
| `category` | VARCHAR | |
| `tech_stack` | TEXT | |
| `comment` | TEXT | |
| `status` | VARCHAR | 'sent', 'got response', 'not interested', 'meeting set', 'offer', 'rejected', 'other'|
| `sent_date` | DATE | |
| `response_date` | DATE | |
| `link` | TEXT | |
| `title` | VARCHAR | |
| `location` | VARCHAR | |
| `location_type` | VARCHAR | 'remote', 'office', 'hybrid' |
| `salary` | TEXT | |
| `salary_type` | VARCHAR | 'hourly-b2b', 'hourly-uop', 'monthly-b2b', 'monthly-uop', 'yearly-b2b', 'yearly-uop' |
| `years_of_experience` | TEXT | |
| `company` | VARCHAR | |
| `company_link` | VARCHAR | |
| `company_description` | TEXT | |
| `responsibilities` | TEXT | |
| `requirements` | TEXT | |
| `benefits` | TEXT | |
| `body` | TEXT | raw html |
| `full_offer` | TEXT | |
| `date_of_access` | DATE | |

## Scripts Usage

### 1. Initialize Database
Sets up the PostgreSQL database and `job_offers` table.
```bash
python init_db.py
```

### 2. Clean Links
Removes duplicates and cleans URL parameters from a list of links.
```bash
python links-cleener.py input_file.txt [output_file.txt]
```

### 3. Scrape a Single Job
Scrapes a job page and prints the data to the console (JSON format).
```bash
python scrape_job.py <url>
```

### 4. Save Job to Database
Scrapes a job page and saves it to the `job_offers` table.
```bash
python save_to_db.py <url>
```

### 5. Reporting
Prints the titles of all jobs currently in the database.
```bash
python reporting.py
```

## How to Use (Workflow)

1. **Prepare your input file**
   - Place your file with job links (one per line) in the project directory.

2. **Run the cleaner script**
   - Open a terminal in the project directory.
   - To clean a file in-place:
     ```
     python links-cleener.py nofluff.txt
     ```
   - To clean and write to a new file:
     ```
     python links-cleener.py nofluff.txt cleaned_nofluff.txt
     ```

3. **Result**
   - The output file will contain unique links with postfixes removed.



**Planned modules:**
- if link is to the same page with just different parameter, append it
- add subcategories
- learning how to use rabbitmq
- Asynchronous queue and scraper
- Reporting and analytics (graphs, word clouds, salary stats)


# Full-Stack - Java, Full-Stack - .Net, Full-Stack - Node.js, Full-stack - Python, Data, Manager/PM,