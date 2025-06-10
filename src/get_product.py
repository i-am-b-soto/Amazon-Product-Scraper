#import random
from bs4 import BeautifulSoup
from .AmazonProduct import AmazonProduct
#from .selenium_behavior import wait_for_product_page_load, human_action


def get_type_of_product_page(soup):
    """
        For now, return "regular"
    """
    return "regular"


def get_price_regular(soup):
    """
    
    """
    whole_number = "00"
    decimal_number = "00"

    whole_number_span = soup.find('span', class_='a-price-whole')
    if whole_number_span:
        whole_number = whole_number_span.get_text()
    else:
        pass
        #print("Whole number does not exist")
    
    decimal_number_span = soup.find('span', class_='a-price-fraction')
    if decimal_number_span:
        decimal_number = decimal_number_span.get_text()
    else:
        pass
        #print("Decimal number does not exist")
    
    return "{}{}".format(whole_number, decimal_number)


def get_description_regular(soup):
    text = "N/A"
    description_div = soup.find("div", id="productDescription")

    if description_div:
        text = description_div.get_text()
    else:
        pass
        #print("Can't find description")
    
    return text 


def get_title_regular(soup):
    """
    
    """
    title = "N/A"
    h1_title = soup.find("h1", id="title")
    if h1_title:
        title_span = h1_title.find("span", id="productTitle")
        if title_span:
            title = title_span.get_text().strip()
        else:
            pass
            #print("No title span")
    else:
        raise Exception("Cannot find title")
        #print("No h1 title")

    return title 


def scrape_regular_product(soup, product_url):
    """
        Scrape a product from a 'regular' Amazon page. Return the goodies
    """
    title = get_title_regular(soup)
    price = get_price_regular(soup)
    description = get_description_regular(soup)

    p = AmazonProduct(title=title, price=price, description=description, 
                      url=product_url)

    return p



def scrape_product(html, product_url):
    """

    """
    soup = BeautifulSoup(html, "html.parser")
    p_type = get_type_of_product_page(soup)

    if p_type == "regular":
        a = scrape_regular_product(soup, product_url)
    
    return a
    # Todo: Other types of product pages


async def get_product(page, product_url):
    """
        Given a list of items, either from a search result or category, return a representation of 
            an Amazon product. Or None if the page couldn't be accessed
    """
    await page.locator("h1#title").wait_for(state="visible", 
                                            timeout=6000)       

    html = await page.content()
    
    p = scrape_product(html, product_url)

    #human_action(driver, random.randint(0, 8))

    return p


if __name__ == "__main__":
    pass

    #print(list_of_product_urls)
    