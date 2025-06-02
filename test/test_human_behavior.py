import undetected_chromedriver as uc
from src.selenium_options import custom_options
from src.selenium_behavior import human_action


if __name__ == "__main__":
    driver = uc.Chrome(options=custom_options())
    driver.get("https://www.amazon.com/ASTRO-Gaming-Wireless-Headset-PlayStation-Console/dp/B08DHH74JQ")
    for num in range(8):
        human_action(driver, num)