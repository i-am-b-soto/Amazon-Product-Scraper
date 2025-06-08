import asyncio
from apify import Actor
from crawlee import Request
from apify.storages import Dataset, RequestQueue
from playwright.async_api import async_playwright
from .product_list import get_product_urls
from .get_product import get_product


CONCURRENCY = 5  # Number of parallel pages
SEMAPHORE = asyncio.Semaphore(CONCURRENCY)


async def handle_product_page(page, dataset):
    product = get_product(page)
    await Actor.push_data(product.to_json())


async def handle_list_page(page, queue):
    # Queue product links
    (product_urls, next_page_url) = await get_product_urls(page)
    for url in product_urls:
        await queue.add_request(Request.from_url(url=url, label="PRODUCT"))

    # Queue next page
    if next_page_url is not None:
        await queue.add_request(Request.from_url(url=url, laebl="LIST"))


async def process_request(queue, dataset, context, request):
    async with SEMAPHORE:
        page = await context.new_page()
        try:
            await page.goto(request["url"], timeout=60000)
            label = request["user_data"].get("label")

            if label == "LIST":
                await handle_list_page(page, queue)
            elif label == "PRODUCT":
                await handle_product_page(page, dataset)

            await queue.mark_request_handled(request)
        except Exception as e:
            print(f"[ERROR] {request['url']}: {e}")
            await queue.reclaim_request(request)
        finally:
            await page.close()


async def main():
    async with Actor:
        queue = await RequestQueue.open(name='Amazon-product-urls')
        dataset = await Dataset.open()

        # Seed if empty
        if await queue.get_handled_count() == 0:
            await queue.add_request(Request.from_url(url="https://www.amazon.com/s?k=gaming+headsets", label="LIST"))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context()

            tasks = []
            while True:
                request = await queue.fetch_next_request()
                if not request:
                    break
                task = asyncio.create_task(
                    process_request(queue, dataset, context, request)
                )
                tasks.append(task)

                # Wait for all concurrent tasks to finish before continuing
                if len(tasks) >= CONCURRENCY:
                    await asyncio.gather(*tasks)
                    tasks = []

            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)

            await browser.close()



"""

from __future__ import annotations
import threading

from apify import Actor


from . import thread_manager


async def main() -> None:

    async with Actor:
        # Retrieve the input object for the Actor. The structure of input is defined in input_schema.json.
        actor_input = await Actor.get_input()
        url = actor_input.get('url')
        #print(url)
        if not url:
            raise ValueError('Missing "url" attribute in input!')
        
        t = threading.Thread(target=thread_manager.start, args=(url,))
        t.start()

        for product in thread_manager.scraped_amazon_products():
            await Actor.push_data(product.to_json())


"""