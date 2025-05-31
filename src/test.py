
from .get_product_urls import get_product_urls

from selenium import webdriver
from .selenium_options import custom_options

if __name__ == "__main__":
    """
        Step 1) We are trying to assess exactly how many product urls are returned from this call
    """
    driver = webdriver.Chrome(options=custom_options())
    list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=gaming+headsets&_encoding=UTF8", driver)
    
    with open("product_url_results.txt", "w") as f:
        for product_url in list_of_product_urls:
            f.write("{}\n".format(product_url))
            print(product_url)

    print(len(list_of_product_urls))
    
