
from src.get_product_urls import get_product_urls
from src.selenium_adapter import get_driver


"""
URLS to try: 
https://www.amazon.com/s?k=electroinc+tablets&_encoding=UTF8

https://www.amazon.com/s?k=gaming+headsets&_encoding=UTF8
"""

if __name__ == "__main__":
    """
        Step 1) We are trying to assess exactly how many product urls are returned from this call
    """
    driver = get_driver()
    list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=electroinc+tablets&_encoding=UTF8", driver)
    
    with open("product_url_results.txt", "w") as f:
        for product_url in list_of_product_urls:
            f.write("{}\n".format(product_url))
            print(product_url)

    #print(len(list_of_product_urls))
    
