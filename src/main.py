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


CONCURRENCY = 8  # Number of parallel pages
MAX_IDLE_CYCLES = 120 # Number of seconds to wait to pull from the queue
REQUEST_TIMEOUT = 8000 # Num of seconds to wait for a single page
# NUM_CONTEXTS = 8 # Number of contexts to have
# NUM_BROWSERS = NUM_CONTEXTS
# CONTEXTS = [] # Global list of contexts
# BROWSERS = []


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


async def process_request(queue, pw, proxy_info, request, semaphore):
    """
        Process a request from the queue
    """
    async with semaphore:
        browser = await get_new_browser(pw, proxy_info)
        context = await browser.new_context(user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                viewport={"width": 1920, "height": 1080},
                is_mobile=False,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
                }
        )
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
            Actor.log.info("✅ Successfully handled request: {}".format(request.url))

        except Exception as e:
            Actor.log.error(e)
            Actor.log.info("Num retries: {}".format(request.user_data.get("retries", 0)))
            retries = request.user_data.get("retries", 0)
            Actor.log.warning(f"Error on {reader_friendly_url} (attempt {retries + 1}): {e}")
            
            if retries < 2:
                request.user_data["retries"] = retries + 1
                Actor.log.info(f"Retrying {reader_friendly_url} (retry {retries + 1})")                
                await asyncio.sleep(2 ** retries)
                await queue.reclaim_request(request)

            else:
                Actor.log.error(f"Failed permanently: {reader_friendly_url} after {retries + 1} attempts")

        finally:
            await page.close()
            await context.close()
            await browser.close()



async def get_new_proxy(proxy_info):
    """
    
    """
    proxy_url = await proxy_info.new_url()

    parsed = urlparse(proxy_url)

    proxy_server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    #proxy_server = proxy_url
    proxy_username = parsed.username
    proxy_password = parsed.password

    return (proxy_server, proxy_username, proxy_password)


async def get_new_browser(pw, proxy_info):
    """

    """
    (proxy_server, proxy_username, proxy_password) = await get_new_proxy(proxy_info)
    browser = await pw.chromium.launch(headless=False, proxy={"server": proxy_server, 
                                                              "username": proxy_username, 
                                                              "password": proxy_password})
    #browser = await pw.chromium.launch(headless=False)
    return browser


async def main():
    """

    """
    idle_cycles = 0
    semaphore = asyncio.Semaphore(2)

    async with Actor:
        queue = await RequestQueue.open()
        proxy_info = await Actor.create_proxy_configuration(groups=["RESIDENTIAL"], country_code='US')        


        if await queue.get_handled_count() == 0:
            r = Request.from_url(url="https://www.amazon.com/s?k=cooker&_encoding=UTF8", label="LIST")
            add_request_info = await queue.add_request(r)
            Actor.log.info(f'Add request info: {add_request_info}')

        async with async_playwright() as pw:
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
                else:
                    idle_cycles = 0

                #Actor.log.info(f'Processing request from Queue: {AmazonProduct.fix_url(request.url)}')

                task = asyncio.create_task(
                    process_request(queue, 
                                    pw,
                                    proxy_info,
                                    request, 
                                    semaphore)
                )
                tasks.append(task)


            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)
            