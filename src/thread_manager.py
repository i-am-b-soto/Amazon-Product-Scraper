import threading
import queue
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from get_product_urls import get_product_urls
from get_product import get_product
from selenium_options import custom_options
from project_globals import NUM_CONSUMERS, FIRST_LIST_PAGE_LOADED, PRODUCT_QUEUE

# Assuming these two functions are defined by you:
# def get_product_urls(listing_url): -> returns list of URLs
# def get_product(product_url): -> returns parsed product data

product_url_queue = queue.Queue()
producers_done = threading.Event()


def scraped_amazon_products(timeout=2):
    """
        Iterable of amazon products
    """
    while True:
        try:
            product = PRODUCT_QUEUE.get(timeout=timeout)
            yield product
        except Exception:
            if producers_done.is_set() and PRODUCT_QUEUE.empty():
                break

def producer(listing_url):
    """
    
    """
    driver = webdriver.Chrome(options=custom_options())

    urls = get_product_urls(listing_url)
    for url in urls:
        product_url_queue.put(url)
    
    producers_done.set()
    
    # Signal to consumers that producer is done
    for _ in range(NUM_CONSUMERS):
        product_url_queue.put(None)
    
    driver.quit()


def consumer(thread_id):
    driver = webdriver.Chrome(options=custom_options())

    while True:
        url = product_url_queue.get()
        if url is None:
            # Signal to terminate this thread
            break
        try:
            product_data = get_product(url, driver)
            PRODUCT_QUEUE.put(product_data)
        except Exception as e:
            print(f"Error in Consumer-{thread_id} with URL {url}: {e}")

    driver.quit()


def start(listing_url):

    # Start the producer thread
    producer_thread = threading.Thread(target=producer, args=(listing_url,))
    producer_thread.start()

    FIRST_LIST_PAGE_LOADED.wait() # Wait for the first page of product urls to be scraped
 
    # Start the consumer threads
    consumer_threads = []
    for i in range(NUM_CONSUMERS):
        t = threading.Thread(target=consumer, args=(i,))
        t.start() 
        consumer_threads.append(t)

    # Wait for producer to finish
    producer_thread.join()

    # Wait for all consumers to finish
    for t in consumer_threads:
        t.join()

    print("All threads finished.")
    print(f"Scraped {len(scraped_products)} products.")


if __name__ == "__main__":
    start()