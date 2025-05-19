from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from selenium_options import custom_options


def get_driver_path():
    return "/home/brian/chrome-driver/chrome-linux64/chrome"


def wait_for_list_page_load(driver):
    # Step 1: Wait for full page load (HTML + JS-ready)
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # Step 2: Wait for a key Amazon element (e.g., search result block)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
    )


def get_next_page_url(html):
    """
    
    """
    soup = BeautifulSoup(html, "html.parser")
    pagination_strip = soup.find("span", class_="s-pagination-strip")
    next_page_url = "https:/www.amazon.com"
    if pagination_strip:
        next_button = pagination_strip.find("a", class_="s-pagination-next")
        if next_button and 'href' in next_button.attrs:
            next_page_url += next_button["href"]
    if next_page_url == "https:/www.amazon.com":
        return None
    return next_page_url


def what_type_of_list(soup):
    list_items = soup.find_all("div", attrs={"role": "listitem"})
    li = list_items[0]

    if li.find("div", class_="puis-card-container"):
        return "rows"
    else:
        return "grid"


def scrape_rows(soup):
    list_items = soup.find_all("div", attrs={"role": "listitem"})

    links = []
    c = 0
    for div in list_items:
        card_container = div.find("div", class_="puis-card-container")
        if div.find("span", string="sponsored") is not None:
           
            continue
        if card_container:

            a_tag = card_container.find("a", class_="a-link-normal")
            if a_tag and 'href' in a_tag.attrs:
                link_string = a_tag['href']
                if link_string.startswith("/sspa"):
                    pass
                else:
                    links.append(link_string)
    
    return links


def scrape_grid(soup):
    list_items = soup.find_all("div", attrs={"role": "listitem"})

    links = []

    for div in list_items:
        span = div.find("span", attrs={"data-component-type": "s-product-image"})
        if div.find("span", string="sponsored") is not None:
            continue
        if span:
            
            a_tag = span.find("a", class_="a-link-normal")
            if a_tag and 'href' in a_tag.attrs:
                link_string = a_tag['href']
                if link_string.startswith("/sspa"):
                    pass
                else:
                    links.append(link_string)
    
    return links  


def scrape_list_page(html):
    soup = BeautifulSoup(html, "html.parser")
    page_type = what_type_of_list(soup)

    urls_on_page = []

    if page_type == "grid":
        urls_on_page = scrape_grid(soup)
    elif page_type == "rows":
        urls_on_page = scrape_rows(soup)
    
    return urls_on_page


def get_product_urls(list_url):
    """
        Given a list of items, either from a search result or category, return a list of all dem urls
    """
    driver = webdriver.Chrome(options=custom_options())

    driver.get(list_url)
    wait_for_list_page_load(driver)
    html = driver.page_source
    total_urls = scrape_list_page(html)
    next_page_url = get_next_page_url(html)
    current_page = 1
    print("Current page: ", current_page)

    while next_page_url is not None:
        # Get page source
        current_page += 1
        driver.get(next_page_url)
        wait_for_list_page_load(driver)    
        html = driver.page_source
        total_urls.extend(scrape_list_page(html))
        next_page_url = get_next_page_url(html)
        print("Current page: ", current_page)

    
    #driver.exit()
    return total_urls


if __name__ == "__main__":
    list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=Shoes&rh=p_36%3A-5000&_encoding=UTF8")

    #print(list_of_product_urls)
    