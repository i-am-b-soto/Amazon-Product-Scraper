"""
    Test the project end-to-end
"""

import threading
from src import thread_manager
import json


if __name__ == "__main__":
    t = threading.Thread(target=thread_manager.start, args=("https://www.amazon.com/s?k=electroinc+tablets&_encoding=UTF8",))
    t.start()

    
   
    with open("Aquired-Amazon-products.txt", "w") as f:
        print("Entering the file")
        for product in thread_manager.scraped_amazon_products():
            f.write(json.loads(product.to_json()))
            print("" + json.loads(product.to_json()))
