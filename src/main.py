import asyncio
import random
from apify import Actor
from apify.storages import RequestQueue
from urllib.parse import urlparse
from crawlee import Request
from playwright.async_api import async_playwright

from .product_list import get_product_urls
from .get_product import get_product
from .AmazonProduct import AmazonProduct


CONCURRENCY = 5  # Number of parallel pages
MAX_IDLE_CYCLES = 60 # Number of seconds to wait to pull from the queue
REQUEST_TIMEOUT = 8000 # Num of seconds to wait for a single page
NUM_CONTEXTS = 8 # Number of contexts to have
NUM_BROWSERS = NUM_CONTEXTS
CONTEXTS = [] # Global list of contexts
BROWSERS = []


def random_user_agent():
    """
    
    """
    user_agents = [
        # Desktop Chrome user agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        # Mobile Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        # Firefox desktop
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
        # Add more user agents as you like
    ]
    return random.choice(user_agents)


def random_viewport():
    """
    
    """
    viewports = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 920},
        {"width": 1440, "height": 900},
        {"width": 1200, "height": 1000},
        {"width": 1280, "height": 800}
    ]
    return random.choice(viewports)


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
        requests.append(
            Request.from_url(url=AmazonProduct.fix_url(url), label="PRODUCT"))
    
    Actor.log.info("Adding {} urls to queue".format(len(requests)))
    await queue.add_requests_batched(requests)

    # Queue next page
    if next_page_url is not None:
        await queue.add_request(
            Request.from_url(url=AmazonProduct.fix_url(url), label="LIST"))


async def process_request(queue, context, request, context_queue):
    """
        Process a request from the queue
    """

    page = await context.new_page()
    reader_friendly_url = AmazonProduct.fix_url(request.url)
    try:
        await page.goto(request.url, timeout=REQUEST_TIMEOUT, 
                        wait_until="domcontentloaded")
        label = request.label

        if label == "LIST":
            await handle_list_page(page, queue)

        elif label == "PRODUCT":
            await handle_product_page(page, request.url)

        await queue.mark_request_as_handled(request)
        Actor.log.info("Handled request: {}".format(request.url))

    except Exception as e:
        retries = request.user_data.get("retries", 0)
        Actor.log.warning(f"Error on {reader_friendly_url} \
                            (attempt {retries + 1}): {e}")
        
        if retries < 2:
            request.user_data["retries"] = retries + 1
            Actor.log.info(f"Retrying {reader_friendly_url} \
                            (retry {retries + 1})")                
            await asyncio.sleep(2 ** retries)
            await queue.reclaim_request(request)

        else:
            Actor.log.error(f"Failed permanently: {reader_friendly_url} after \
                            {retries + 1} attempts")

    finally:
        await page.close()
        await context_queue.put(context)


async def get_new_proxy():
    """
    
    """
    proxy_info = await Actor.create_proxy_configuration(groups=["RESIDENTIAL"], 
                                                        country_code='US')
    proxy_url = await proxy_info.new_url()

    parsed = urlparse(proxy_url)

    #proxy_server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    proxy_server = proxy_url
    proxy_username = parsed.username
    proxy_password = parsed.password

    return (proxy_server, proxy_username, proxy_password)


async def get_new_browser(pw):
    """

    """
    (proxy_server, proxy_username, proxy_password) = await get_new_proxy()
    #browser = await pw.chromium.launch(headless=False, proxy={"server": "http://groups-RESIDENTIAL,country-US:apify_proxy_hIqCMm9uxsg3o2TfOuBXv9fjJA95eR1LqA6v@proxy.apify.com:8000", 
    #                                                          "username": proxy_username, 
    #                                                          "password": "apify_proxy_hIqCMm9uxsg3o2TfOuBXv9fjJA95eR1LqA6v"})
    #browser = await pw.chromium.launch(headless=False)
    browser = await pw.chromium.launch(headless=False, proxy={"server": 
                                                              proxy_server})
    return browser


async def generate_contexts(pw):
    """
    
    """
    for _ in range(NUM_CONTEXTS):
        browser = await get_new_browser(pw)
        context = await browser.new_context(
            user_agent=random_user_agent(),
            viewport=random_viewport(),
            locale="en-US",
            java_script_enabled=True,
            timezone_id="America/New_York"
        )
        CONTEXTS.append(context)
        BROWSERS.append(browser)


async def close_contexts():
    """
    
    """
    for i in range(NUM_CONTEXTS):
        await CONTEXTS[i].close()
        await BROWSERS[i].close()


async def main():
    """

    """
    idle_cycles = 0
    context_queue = asyncio.Queue()

    async with Actor:
        queue = await RequestQueue.open()

        if await queue.get_handled_count() == 0:
            r = Request.from_url(url="https://www.amazon.com/s?k=fitness+equipment&_encoding=UTF8", label="LIST")
            add_request_info = await queue.add_request(r)
            Actor.log.info(f'Add request info: {add_request_info}')
            processed_request = await queue.get_request(add_request_info.id)
            Actor.log.info(f'Processed request: {processed_request}')

        async with async_playwright() as pw:
            tasks = []

            await generate_contexts(pw) # Generate contexts to use
            for context in CONTEXTS:
                await context_queue.put(context)
            
            while not await queue.is_finished():
                request = await queue.fetch_next_request()
                if request is None:
                    idle_cycles += 1
                    
                    if idle_cycles >= MAX_IDLE_CYCLES:
                        Actor.log.warning("Queue idle too long. Exiting")
                        break

                    await asyncio.sleep(1)
                    continue

                Actor.log.info(f'Processing request from Queue: \
                               {AmazonProduct.fix_url(request.url)}...')
                
                try:
                    context = await asyncio.wait_for(context_queue.get(), 
                                                     timeout=REQUEST_TIMEOUT + 5.00)
                except asyncio.TimeoutError:
                    Actor.log.error("Timeout waiting for context")
                    break
                else:
                    task = asyncio.create_task(
                        process_request(queue, 
                                        context, 
                                        request, 
                                        context_queue)
                    )
                    tasks.append(task)


            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)
            
            # Close all contexts
            await close_contexts()