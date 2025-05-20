from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_list_page_load(driver):
    WebDriverWait(driver, 2).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
    )


def wait_for_product_page_load(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
    except Exception as e:
        print("Timed out waiting for page to load.", e)