import asyncio
from apify import Actor
from crawlee import Request
from apify.storages import Dataset, RequestQueue
from playwright.async_api import async_playwright
from .product_list import get_product_urls
from .get_product import get_product


CONCURRENCY = 5  # Number of parallel pages
MAX_IDLE_CYCLES = 30


CONTEXT_POOL_SIZE = 5
CONTEXTS = []



async def create_contexts(browser):
    
    for _ in range(CONTEXT_POOL_SIZE):
        context = await browser.new_context(
            user_agent=random_user_agent(),
            viewport=random_viewport(),
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True
        )
        CONTEXTS.append(context)


async def handle_product_page(page, product_url):
    """
        Handle a product page request
    """
    product = await get_product(page, product_url)
    await Actor.push_data(product.to_json())


async def handle_list_page(page, queue):
    """
        Handle a list page request
    """
    (product_urls, next_page_url) = await get_product_urls(page)
    requests = []
    for url in product_urls:
        requests.append(Request.from_url(url=url, label="PRODUCT"))
    
    await queue.add_requests_batched(requests)

    # Queue next page
    if next_page_url is not None:
        await queue.add_request(Request.from_url(url=url, label="LIST"))


async def process_request(queue, browser, request, semaphore):
    """
        Process a request from the queue
    """
    async with semaphore:
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            viewport={'width': 1280, 'height': 800},
            locale="en-US",
            java_script_enabled=True,
            timezone_id="America/New_York"
        )

        page = await context.new_page()
        try:
            await page.goto(request.url, timeout=60000, wait_until="domcontentloaded")
            label = request.label

            if label == "LIST":
                await handle_list_page(page, queue)

            elif label == "PRODUCT":
                await handle_product_page(page, request.url)

            await queue.mark_request_as_handled(request)
            Actor.log.info("Handled request: {}".format(request.url))

        except Exception as e:
            retries = request.user_data.get("retries", 0)
            Actor.log.warning(f"Error on {request.url} (attempt {retries + 1}): {e}")
            
            if retries < 2:
                request.user_data["retries"] = retries + 1
                await queue.reclaim_request(request)
                Actor.log.info(f"Retrying {request.url} 
                               (retry {retries + 1})")
            else:
                Actor.log.error(f"Failed permanently: {request.url} after 
                                {retries + 1} attempts")
                await queue.drop_request(request) 

        finally:
            await page.close()
            await context.close()


async def main():
    SEMAPHORE = asyncio.Semaphore(CONCURRENCY)
    idle_cycles = 0

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
            browser = await pw.chromium.launch(headless=False)

            tasks = []
            while not await queue.is_finished():
                request = await queue.fetch_next_request()

                if request is None:
                    idle_cycles += 1
                    
                    if idle_cycles >= MAX_IDLE_CYCLES:
                        Actor.log.warning("Queue idle too long. Exiting")
                        break

                    await asyncio.sleep(1)
                    continue

                Actor.log.info(f'Pulled Request from Queue: {request.url}...')

                task = asyncio.create_task(
                    process_request(queue, browser, request, 
                                    SEMAPHORE)
                )

                tasks.append(task)


            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)

            await browser.close()