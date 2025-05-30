import schedule
import time
from scanner.port_scanner import run_scan


def schedule_scan(target, ports, interval):
    """Schedule a scan to run at regular intervals."""
    def job():
        print(f"Running scheduled scan for {target} on ports {ports}.")
        run_scan(target, ports)

    schedule.every(interval).seconds.do(job)

    print(f"Scheduled scan for {target} every {interval} seconds.")
    while True:
        schedule.run_pending()
        time.sleep(1)
