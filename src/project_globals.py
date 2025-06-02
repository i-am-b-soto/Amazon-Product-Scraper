import threading
import queue

FIRST_LIST_PAGE_LOADED = threading.Event()
FIRST_PRODUCT_AVAILABLE = threading.Event()
PRODUCT_QUEUE = queue.Queue()
NUM_CONSUMERS = 5


