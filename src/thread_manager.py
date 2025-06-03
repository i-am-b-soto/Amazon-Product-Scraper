import threading
import queue
import time


from .get_product_urls import get_product_urls
from .get_product import get_product
from .selenium_adapter import get_driver
from .project_globals import (NUM_CONSUMERS, FIRST_LIST_PAGE_LOADED,
                    PRODUCT_QUEUE)

# Assuming these two functions are defined by you:
# def get_product_urls(listing_url): -> returns list of URLs
# def get_product(product_url): -> returns parsed product data

product_url_queue = queue.Queue()
producers_done = threading.Event()
product_end_marker = object()  # To signal completion

products_processed = 0
lock = threading.Lock()

def increment():
    global products_processed
    with lock:
        products_processed += 1


def get_products_processed():
    with lock:
        return products_processed


def scraped_amazon_products(timeout=10):
    """
        Iterable of amazon products
    """
    #print("Entering scraped amazon product")
    count = 0
    while True:
        count += 1
        #print("========\nAttempt {}\n=======".format(count))
        try:
            product = PRODUCT_QUEUE.get(timeout=timeout)
            yield product
        except Exception:
            #print("scraped amazon product exception reached.")
            if producers_done.is_set() and PRODUCT_QUEUE.empty():
                #print("========\nProducers is all done and the product queue is empty\n============")
                break


def producer(listing_url):
    """
    
    """
    driver = get_driver()

    urls = get_product_urls(listing_url, driver)
    for url in urls:
        product_url_queue.put(url)

    producers_done.set()
    
    # Signal to consumers that producer is done
    for _ in range(NUM_CONSUMERS):
        product_url_queue.put(None)
    
    driver.quit()


def consumer(thread_id):
    """

    """
    print("Thread {} has started".format(thread_id))
    driver = get_driver()

    while True:
        url = product_url_queue.get()
        if url is None:
            # Signal to terminate this thread
            break
        try:
            product_data = get_product(url, driver)
            if product_data:

                PRODUCT_QUEUE.put(product_data)
                increment()
                print("{} products processed".format(get_products_processed()))
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

    start_time = time.time()

    # Wait for producer to finish
    producer_thread.join()

    # Wait for all consumers to finish
    for t in consumer_threads:
        t.join()
    
    end_time = time.time()

    print("All threads finished. Total time elapsed: {}"
          .format(end_time - start_time))


if __name__ == "__main__":
    start()