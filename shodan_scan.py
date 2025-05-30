from integrations.shodan_integration import shodan_search


def run_shodan_scan(target):
    print(f"Running Shodan scan on {target}")
    results = shodan_search(target)
    if not results:
        print("No results found or error occurred.")
        return
    for item in results:
        print(f"Port: {item['port']}, Banner: {item['banner']}, "
              f"Timestamp: {item['timestamp']}")
