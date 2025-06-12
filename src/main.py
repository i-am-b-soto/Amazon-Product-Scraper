import asyncio
from apify import Actor
from crawlee import Request
from apify.storages import RequestQueue
from urllib.parse import urlparse

from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError, Error as playwright_error
from request_handlers import handle_product_page, handle_list_page


SEMAPHORE_CONCURRENCY = 8
MAX_IDLE_CYCLES = 120
REQUEST_TIMEOUT = 12000
BANNED_DOMAINS = ["media-amazon.com", "ssl-images-amazon.com", 
                  "amazon-adsystem.com"]


async def block_images(route, request):
    """

    """
    if route.request.resource_type in {"image", "media"}:
        await route.abort()
    else:
        l = False
        for domain in BANNED_DOMAINS:
            if request.url.find(domain) != -1:
                await route.abort()
                l = True
        else:
            if not l:
                await route.continue_()


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
                viewport={"width": 1420, "height": 1080},
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
        try:
            await page.route("**/*", block_images)          
            await page.goto(request.url, timeout=REQUEST_TIMEOUT, 
                            wait_until="domcontentloaded")
            label = request.label
            if label == "LIST":
                await handle_list_page(page, queue)

            elif label == "PRODUCT":
                await handle_product_page(page, request.url)
            await queue.mark_request_as_handled(request)
            Actor.log.info("✅ Successfully processed request: {}"
                           .format(request.url))

        except (TimeoutError, playwright_error) as e: 
            # Catch timeout & Playwright errors
            retries = request.user_data.get("retries", 0)
            Actor.log.warning("Error on {} (attempt {}): {}"
                              .format(request.url, retries + 1, e))
            if retries < 2:
                request.user_data["retries"] = retries + 1
                Actor.log.info("Retrying {} (retry {})"
                               .format(request.url, retries + 1))
                await asyncio.sleep(1)
                await queue.reclaim_request(request)
            else:
                await queue.mark_request_as_handled(request)
                Actor.log.error("❌ Failed permanently: {} after {} attempts"
                                .format(request.url, retries + 1))

        except Exception as e:
            # All other errors will fall under here
            await queue.mark_request_as_handled(request) # Don't bother with a re-try
            Actor.log.error("❌ Failed permanently: {} {}"
                            .format(request.url, e))            

        finally:
            await page.close()
            await context.close()
            await browser.close()


async def get_new_proxy(proxy_info):
    """
        return dict
    """
    proxy_url = await proxy_info.new_url()
    parsed = urlparse(proxy_url)
    return {
        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
        "username": parsed.username,
        "password": parsed.password,
    }


async def get_new_browser(pw, proxy_info):
    """

    """
    (proxy_server, proxy_username, proxy_password) = await get_new_proxy(proxy_info)
    #browser = await pw.chromium.launch(headless=False, proxy=get_new_proxy(proxy_info))
    browser = await pw.chromium.launch(headless=False)
    return browser


async def main():
    """

    """
    idle_cycles = 0
    semaphore = asyncio.Semaphore(SEMAPHORE_CONCURRENCY)

    async with Actor:
        queue = await RequestQueue.open()
        proxy_info = await Actor.create_proxy_configuration(
            groups=["RESIDENTIAL"], country_code='US')        
        actor_input = await Actor.get_input() or {}
        start_list_url = actor_input.get('url')

        if start_list_url is None:
            Actor.log.error("Please enter a product list url from Amazon")
            raise Exception("No Start Url found")

        r = Request.from_url(url=start_list_url, label="LIST")
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