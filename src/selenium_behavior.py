import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin


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
    """
        Random short sleep to mimic thinking time.
    """
    time.sleep(random.uniform(a, b))


def human_scroll(driver, max_scrolls=5, 
                 use_mouse_movement=True, 
                 use_keyboard_scroll=True):
    """
        Simulates a more human-like scrolling behavior.
    """
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll = 0

    actions = ActionChains(driver)

    for _ in range(max_scrolls):
        # Optional mouse movement
        if use_mouse_movement and random.random() < 0.7:
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            try:
                actions.move_by_offset(x_offset, y_offset).perform()
                actions.reset_actions()
            except Exception:
                pass  # in case offset is out of bounds        
        
        # Occasionally pause longer as if user is reading
        if random.random() < 0.2:
            human_sleep(1.5, 3.5)

        # Choose scroll method
        if use_keyboard_scroll and random.random() < 0.1:
            actions.send_keys(Keys.PAGE_DOWN).perform()
            scroll_by = 600  # Approximate for PAGE_DOWN
        else:        
            # Scroll amount with variation
            scroll_by = random.choice([
                random.randint(100, 300),
                random.randint(300, 900),
                -random.randint(50, 200) if random.random() < 0.1 else 0  # occasionally scroll up
            ])
            actions.scroll_by_amount(0, scroll_by)
            actions.reset_actions()

        current_scroll += scroll_by
        current_scroll = max(0, current_scroll)

        # Simulate scroll hesitation
        human_sleep(0.1, 2)

        # Stop if we've reached near the bottom
        if current_scroll + random.randint(100, 500) > scroll_height:
            human_sleep(1, 3)


def human_hover(driver, max_hovers=2):
    """
        Simulate a realistic human-like hover over links.
    """
    links = driver.find_elements(By.TAG_NAME, "a")
    visible_links = [link for link in links if link.is_displayed() and 
                     link.get_attribute("href")]

    if not visible_links:
        return

    # Number of hovers before stopping
    hover_count = random.randint(1, max_hovers)

    actions = ActionChains(driver)

    for _ in range(hover_count):
        link = random.choice(visible_links)

        try:
            # Simulate approach by moving near the element first
            actions.move_to_element_with_offset(link, random.randint(-30, 30), random.randint(-10, 10)).perform()
            human_sleep(0.1, 0.4)

            # Then hover directly on the element
            actions.move_to_element(link).perform()

            # Simulate hesitation/read time
            human_sleep(0.3, 2.0)

            # Optional: sometimes move away without clicking
            if random.random() < 0.3:
                actions.move_by_offset(random.randint(50, 150), random.randint(20, 60)).perform()
                human_sleep(0.1, 0.4)
        except Exception:
            continue  # skip broken elements


def human_click(driver):
    # Collect all clickable elements
    clickables = driver.find_elements(By.XPATH, "//*[self::a or self::button or @onclick]")
    pass


def human_scroll_and_hover(
    driver,
    max_scrolls=5,
    use_mouse_movement=True,
    use_keyboard_scroll=True,
    use_wheel_scroll=True,
    max_hovers=2
):
    """
        Simulates human-like scrolling, then hovers over visible links.
    """
    actions = ActionChains(driver)
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll = 0
    viewport_height = driver.execute_script("return window.innerHeight")

    # ---------- HOVER Elements ----------
    links = driver.find_elements(By.TAG_NAME, "a")
    visible_links = [link for link in links if link.is_displayed() and 
                     link.get_attribute("href")]


    hover_count = random.randint(1, max_hovers)
    
    # ---------- SCROLL ----------
    for _ in range(max_scrolls):
        if use_mouse_movement and random.random() < 0.7:
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            try:
                actions.move_by_offset(x_offset, y_offset).perform()
                actions.reset_actions()
            except Exception as e:
                pass
                #print("Error scrolling mouse {}".format(e))  # skip errors

        if random.random() < 0.2:
            human_sleep(1.5, 3.0)

        scroll_by = random.randint(200, 600)

        if use_wheel_scroll and random.random() < 0.6:
            origin = ScrollOrigin.from_viewport(0, 0)
            try:
                actions.scroll_from_origin(origin, 0, scroll_by).perform()
            except Exception as e:
                print("Error executing wheel {}".format(e))
                driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        elif use_keyboard_scroll and random.random() < 0.5:
            actions.send_keys(Keys.PAGE_DOWN).perform()
            scroll_by = viewport_height
        else:
            driver.execute_script(f"window.scrollBy(0, {scroll_by});")

        current_scroll += scroll_by
        current_scroll = max(0, current_scroll)

        human_sleep(0.2, 0.8)

        # --- Hover ---
        if hover_count > 0:
            link = random.choice(visible_links)
            try:
                # Move near the link first
                actions.move_to_element_with_offset(link, random.randint(-30, 30), 
                                                    random.randint(-10, 10)).perform()
                human_sleep(0.1, 0.4)

                # Then hover directly
                actions.move_to_element(link).perform()
                human_sleep(0.3, 2.0)

                # Occasionally move away
                if random.random() < 0.3:
                    actions.move_by_offset(random.randint(50, 150),
                                          random.randint(20, 60)).perform()
                    human_sleep(0.1, 0.4)

            except Exception:
                pass  # ignore unhoverable elements
            finally: 
                hover_count -= 1

        if current_scroll + 1000 > scroll_height:
            break


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
        human_hover(driver, max_hovers=4)
    if num == 4:
        human_scroll_and_hover(driver, max_scrolls=7, max_hovers=3)
    if num == 5:
        human_scroll_and_hover(driver, max_scrolls=1, max_hovers=3)
    if num == 6:
        human_scroll_and_hover(driver, max_scrolls=3, max_hovers=1)
    if num >= 7:
        human_scroll(driver, 3, True, False)
    