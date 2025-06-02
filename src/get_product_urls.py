import random
from bs4 import BeautifulSoup
from .selenium_behavior import wait_for_list_page_load, human_action
from .project_globals import FIRST_LIST_PAGE_LOADED


def get_next_page_url(html):
    """
        Return the next page in a product list
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
    """
        Determine what type of list the product list page is (currently identified 2 types - Grid and row)
    """
    list_items = soup.find_all("div", attrs={"role": "listitem"})
    li = list_items[0]

    if li.find("div", class_="puis-card-container"):
        return "rows"
    else:
        return "grid"


def scrape_rows(soup):
    """
        Scrape row list page
    """
    list_items = soup.find_all("div", attrs={"role": "listitem"})

    links = []

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
                    links.append("https://www.amazon.com" + link_string)
    
    return links


def scrape_grid(soup):
    """
        Scrape grid list page
    """
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
                    links.append("https://www.amazon.com" + link_string)
    
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


def get_product_urls(list_url, driver):
    """
        Given a list of items, either from a search result or category, return a list of all dem urls
    """

    try:
        driver.get(list_url)
        wait_for_list_page_load(driver)
    except Exception as e:
        print("There was an issue aquiriing the Amazon list url {}: {}"
              .format(list_url, e))
        raise StopIteration
    
    html = driver.page_source

    #with open("super-quick-test-1.html", "w") as f:
    #    f.write(html)

    total_urls = scrape_list_page(html)
    FIRST_LIST_PAGE_LOADED.set()
    next_page_url = get_next_page_url(html)
    current_page = 1
    
    for url in total_urls:
        yield url

    while next_page_url is not None:
        current_page += 1
        
        try:
            driver.get(next_page_url)
            wait_for_list_page_load(driver)
        except Exception as e:
            print("There was an issue aquiriing the Amazon list url{}: {}"
                .format(next_page_url, e))
            raise StopIteration

        html = driver.page_source
        total_urls = scrape_list_page(html)
        next_page_url = get_next_page_url(html)

        human_action(driver, random.randint(0, 8))

        for url in total_urls:
            yield url


if __name__ == "__main__":
    pass
    