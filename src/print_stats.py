import psutil
import os
from apify import Actor


def print_stats():

    process = psutil.Process(os.getpid())

    # CPU usage of current process (over 1 second interval)
    cpu_usage = process.cpu_percent(interval=1)

    # RAM usage of current process
    mem_info = process.memory_info()
    ram_used_mb = mem_info.rss / (1024 ** 2)

    Actor.log.info(f"[Current Process] CPU: {cpu_usage}% | RAM: {ram_used_mb:.2f} MB")