import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


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


def human_sleep(a=0.5, b=2.5):
    """Random short sleep to mimic thinking time."""
    time.sleep(random.uniform(a, b))


def human_scroll(driver, max_scrolls=3):
    """
        Simulates a more human-like scrolling behavior.
    """
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll = 0

    for _ in range(max_scrolls):
        # Occasionally pause longer as if user is reading
        if random.random() < 0.2:
            human_sleep(1.5, 3.5)
        
        # Scroll amount with variation
        scroll_by = random.choice([
            random.randint(100, 300),
            random.randint(300, 900),
            -random.randint(50, 200) if random.random() < 0.1 else 0  # occasionally scroll up
        ])

        driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        current_scroll += scroll_by
        current_scroll = max(0, current_scroll)

        # Simulate scroll hesitation
        human_sleep(0.1, 3)

        # Stop if we've reached near the bottom
        if current_scroll + random.randint(100, 500) > scroll_height:
            human_sleep(1, 3)


def human_hover(driver):
    """Hover over an element (like users do before clicking)."""
    # Find all links
    links = driver.find_elements(By.TAG_NAME, "a")

    # Optional: filter for visible & usable links
    visible_links = [link for link in links if link.is_displayed() and
                     link.get_attribute("href")]
    selected = random.choice(visible_links)
    ActionChains(driver).move_to_element(selected).perform()


def human_click(driver):
    # Collect all clickable elements
    clickables = driver.find_elements(By.XPATH, "//*[self::a or self::button or @onclick]")
    pass


def human_action(driver, num):
    """
        num = 0 -> 9
    """
    if num == 0:
        pass
    if num == 1:
        human_sleep()
    if num == 2:
        human_scroll(driver)
    if num == 3:
        human_hover(driver)
        human_scroll(driver)
    if num == 4:
        human_scroll(driver)
        human_sleep()
    if num == 5:
        human_scroll(driver)
        human_sleep()
        human_hover(driver)
    if num == 6:
        human_hover(driver)
        human_sleep()
        human_scroll(driver)
        human_sleep()
        human_hover(driver)
    if num >= 7:
        human_hover(driver)
        human_sleep()
        human_hover(driver)
        human_scroll(driver)
        human_sleep()