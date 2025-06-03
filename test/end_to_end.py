"""
    Test the project end-to-end
"""

import threading
from src import thread_manager
import json

"""
    Some URLs to use: 
        https://www.amazon.com/s?k=desk
        https://www.amazon.com/s?k=electroinc+tablets&_encoding=UTF8
"""


if __name__ == "__main__":
    t = threading.Thread(target=thread_manager.start, args=("https://www.amazon.com/s?k=desk",))
    t.start()

    
    with open("Aquired-Amazon-products.txt", "w") as f:
        print("Entering the file")
        for product in thread_manager.scraped_amazon_products():
            f.write("{}\n".format(json.dumps(product.to_json())))
