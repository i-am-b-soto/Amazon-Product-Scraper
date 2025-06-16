from bs4 import BeautifulSoup
from src.get_product import get_product
import json

"""
    Some URLS we can try: 
        https://www.amazon.com/BYYBUO-SmartPad-A10-Quad-Core-Touchscreen/dp/B09TQYQL1Z/ref=sr_1_18?_encoding=UTF8&sr=8-18&xpid=9i2Q1Jj8Hn_Sy
"""

def test_asin():
    with open("example_amazon_product.html", "r") as f:
        html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        asin_input = soup.find('input', {'id': 'ASIN'})

        if asin_input and asin_input.has_attr('value'):
            asin = asin_input['value']
            print(f'ASIN: {asin}')
        else:
            print("ASIN not found.")
        

def test_image():

    with open("example_amazon_product.html", "r") as f:
        html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        # Step 1: Find the div
        image_block = soup.find('div', {'id': 'altImages'})

        # Step 2: Find the first li with class "imageThumbnail" inside it
        if image_block:
            thumbnail_li = image_block.find_all('li', class_='imageThumbnail')

            # Step 3: Find the img tag inside the li
            if thumbnail_li and len(thumbnail_li) > 0:
                img_tag = thumbnail_li[0].find('img')
                
                # Step 4: Get the src
                if img_tag and img_tag.has_attr('src'):
                    img_src = img_tag['src']
                    
                else:
                    pass
            else:
                pass
        else:
            pass

def test_get_stars():
    with open("example_amazon_product.html", "r") as f:
        html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        # Step 1: Find the div
        reviews_div = soup.find('div', class_='AverageCustomerReviews')

        # Step 2: Find the span with class "a-icon-alt"
        if reviews_div:
            rating_span = reviews_div.find('span', class_='a-icon-alt')
            if rating_span:
                rating_text = rating_span.get_text(strip=True)
                print(f"Rating: {rating_text.split(' ')[0]}")
            else:
                print("Rating span not found.")
        else:
            print("Reviews div not found.")


def test_get_review_count():
    with open("example_amazon_product.html", "r") as f:
        html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        # Find the span with the specific data-hook
        review_count_span = soup.find('span', attrs={'data-hook': 'total-review-count'})

        # Get the text content
        if review_count_span:
            total_reviews = review_count_span.get_text(strip=True)
            if total_reviews:
                r = total_reviews.strip().split(' ')[0]
            print(f"Total reviews: {total_reviews}")
        else:
            print("Review count span not found.")    


if __name__ == '__main__':
    #product = get_product("https://www.amazon.com/BYYBUO-SmartPad-A10-Quad-Core-Touchscreen/dp/B09TQYQL1Z/ref=sr_1_18?_encoding=UTF8&sr=8-18&xpid=9i2Q1Jj8Hn_Sy", driver)
    #print(json.dumps(product.to_json()))
    #test_elements()
    test_image()
    test_get_stars()
    test_get_review_count()
