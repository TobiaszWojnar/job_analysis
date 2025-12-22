import sys


def clean_links(lines):
    cleaned = set()
    for line in lines:
        url = line.strip().split("?")[0] #removes query parameters
        url = url.split(": ")[0] #removes debug notes why sth was error
        if url:
            cleaned.add(url)
    return list(sorted(cleaned))

def main():
    if len(sys.argv) == 2:
        input_file = output_file = sys.argv[1]
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print(f"Usage: python {sys.argv[0]} <input_file> [output_file]")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned_urls = clean_links(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        for url in cleaned_urls:
            f.write(url + "\n")

if __name__ == "__main__":
    main()