"""Module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations

from apify import Actor
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from httpx import AsyncClient



class AmazonProduct:
    _title = None
    _price = None

    def __init__(self, title, price):
        self._title = title
        self._price = price

    def to_json_(self):
        return {"title": self._title, "price": self._price}


def selenium_options():
    options = Options()
    options.add_argument("--disable-gpu")  # Safe in most headless environments
    options.add_argument("--window-size=1880,1440")  # Explicit viewport size
    options.add_argument("--no-sandbox")  # Required by some container environments
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in containers
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36")


def scrape_product(url):
    driver = webdriver.Chrome(options=selenium_options())

    driver.get(url)

    time.sleep(2)

    # Get page source
    html = driver.page_source

    driver.exit()


async def main() -> None:
    """Define a main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Apify platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        # Retrieve the input object for the Actor. The structure of input is defined in input_schema.json.
        actor_input = await Actor.get_input() or {'url': 'https://apify.com/'}
        url = actor_input.get('url')
        if not url:
            raise ValueError('Missing "url" attribute in input!')
        
        scraped_amazon_products = []

        for product in scraped_amazon_products:
            await Actor.push_data(product.to_json())
