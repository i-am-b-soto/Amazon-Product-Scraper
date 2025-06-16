import asyncio
import random
from bs4 import BeautifulSoup
from .AmazonProduct import AmazonProduct
from .custom_exceptions import ProductNotLoaded


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
        raise ProductNotLoaded("Cannot find title - likely product not loaded")

    return title

def get_asin_regular(soup):
    asin = "N/A"
    asin_input = soup.find('input', {'id': 'ASIN'})

    if asin_input and asin_input.has_attr('value'):
        asin = asin_input['value']
    else:
        pass
        #print("ASIN not found.")

    return asin


def get_image_regular(soup):
    img_src = None
    image_block = soup.find_all('div', class_='imageThumbnail')

    if image_block and len(image_block) > 0:
        img_tag = image_block[0].find('img')

        if img_tag and img_tag.has_attr('src'):
            img_src = img_tag['src']
        else:
            pass

    return img_src


def get_stars_regular(soup):
    r = None
    reviews_div = soup.find('div', class_='AverageCustomerReviews')
    if reviews_div:
        rating_span = reviews_div.find('span', class_='a-icon-alt')
        if rating_span:
            rating_text = rating_span.get_text(strip=True)
            if rating_text:
                r = rating_text.split(' ')[0]
        else:
            pass
    else:
        pass

    return r


def get_review_count_regular(soup):
    r = None
    review_count_span = soup.find('span', attrs={'data-hook': 'total-review-count'})

    if review_count_span:
        total_reviews = review_count_span.get_text(strip=True)
        if total_reviews:
            r = total_reviews.strip().split(' ')[0]
    else:
        pass

    return r      


def scrape_regular_product(soup, product_url):
    """
        Scrape a product from a 'regular' Amazon page. Return the goodies
    """
    asin = get_asin_regular(soup)
    title = get_title_regular(soup)
    image = get_image_regular(soup)
    price = get_price_regular(soup)
    stars = get_stars_regular(soup)
    review_count = get_review_count_regular(soup)
    description = get_description_regular(soup)


    p = AmazonProduct(ASIN=asin, 
                      image=image, 
                      title=title, 
                      price=price,
                      stars=stars,
                      review_count=review_count,
                      description=description, 
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


async def is_valid_page(page, timeout: int = 6000) -> str:
 
    # Create two tasks to wait for either of the two conditions
    product_page_task = asyncio.create_task(
        page.locator("h1#title").wait_for(state="visible", timeout=timeout)
    )
    captcha_task = asyncio.create_task(
        page.wait_for_selector('h4:text("Enter the characters you see below")', timeout=timeout)
    )

    error_img_task = asyncio.create_task(
        page.wait_for_selector('img[alt="Sorry! Something went wrong on our end. Please go back and try again or go to Amazon\'s home page."]', timeout=timeout)
    )        

    done, pending = await asyncio.wait(
        [product_page_task, captcha_task, error_img_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel the task that didn't finish
    for task in pending:
        task.cancel()

    # Determine which condition matched
    if product_page_task in done:
        return True
    elif captcha_task in done:
        return False
    elif error_img_task in done:
        return False


async def get_product(page, product_url):
    """
        Given a list of items, either from a search result or category, return a representation of 
            an Amazon product. Or None if the page couldn't be accessed
    """
    try:
        if await is_valid_page(page):
            pass
        else:
            await asyncio.sleep(random.uniform(1.2, 5.4))
            raise ProductNotLoaded("Blocked")
    except Exception as e:
        raise ProductNotLoaded("Blocked by timeout")

    html = await page.content()
    
    p = scrape_product(html, product_url)

    return p


if __name__ == "__main__":
    pass

    #print(list_of_product_urls)
    