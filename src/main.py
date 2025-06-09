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

    page = await context.new_page()
    try:
        await page.goto(request.url, timeout=60000, wait_until="networkidle")
        #print("request: {}".format(request))
        label = request.label
        #print("label: {}".format(label))

        if label == "LIST":
            (product_urls, next_page_url) = await handle_list_page(page, queue)
        elif label == "PRODUCT":
            await handle_product_page(page, dataset)

        await queue.mark_request_as_handled(request)
    except Exception as e:
        Actor.log.error("ERROR: {} {}".format(request.url, e))
        #await queue.reclaim_request(request)
    finally:
        await page.close()


async def main():
    async with Actor:
        queue = await RequestQueue.open()
        dataset = await Dataset.open()

        # Seed if empty
        if await queue.get_handled_count() == 0:
            r = Request.from_url(url="https://www.amazon.com/s?k=fitness+equipment&_encoding=UTF8", label="LIST")
            add_request_info = await queue.add_request(r)
            Actor.log.info(f'Add request info: {add_request_info}')
            processed_request = await queue.get_request(add_request_info.id)
            Actor.log.info(f'Processed request: {processed_request}')

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context()

            tasks = []
            while not await queue.is_finished():
                request = await queue.fetch_next_request()

                if request is None:
                    await asyncio.sleep(1)
                    continue

                Actor.log.info(f'Pulled Request from Queue: {request.url}...')
                #Actor.log.info(f'Scraping URL {request.url}...')

                # Wait for a semaphore permit
                await SEMAPHORE.acquire()

                task = asyncio.create_task(
                    process_request(queue, dataset, context, request)
                )

                # When done, release the semaphore
                task.add_done_callback(lambda t: SEMAPHORE.release())                

                tasks.append(task)

                """
                # Wait for all concurrent tasks to finish before continuing
                if len(tasks) >= CONCURRENCY:
                    await asyncio.gather(*tasks)
                    tasks = []
                """

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