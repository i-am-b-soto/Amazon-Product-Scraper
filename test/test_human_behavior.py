from selenium import webdriver
from src.selenium_options import custom_options
from src.selenium_behavior import human_action, wait_for_product_page_load





if __name__ == "__main__":
    driver = webdriver.Chrome(options=custom_options())
    driver.get("https://www.amazon.com/ASTRO-Gaming-Wireless-Headset-PlayStation-Console/dp/B08DHH74JQ")
    for num in range(8):
        human_action(driver, num)