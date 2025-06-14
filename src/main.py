import asyncio
import random
from apify import Actor
from crawlee import Request
from apify.storages import RequestQueue

from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError, Error as playwright_error
from .request_handlers import handle_product_page, handle_list_page
from .ProxyManager import ProxyManager
from .BrowserPool import BrowserPool
from .browser_contexts import browser_contexts
from .custom_exceptions import ProductListPageNotLoaded


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


async def process_request(queue, browser_pool, request, semaphore):
    """
        Process a request from the queue
    """
    async with semaphore:
        browser_wrapper = await browser_pool.get_next_browser()
        await browser_wrapper.enter_lock()
        browser = browser_wrapper.get_browser()
        context_config = random.choice(browser_contexts)
        context = await browser.new_context(
            user_agent=context_config["user_agent"],
            locale=context_config["locale"],
            viewport=context_config["viewport"],
            is_mobile=False,
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/"
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

        except (TimeoutError, playwright_error, ProductListPageNotLoaded) as e: 
            # Catch timeout & Playwright errors
            retries = request.user_data.get("retries", 0)
            Actor.log.warning("Error on {} (attempt {}): {}"
                            .format(request.url, retries + 1, e))
            
            await browser_pool.handle_no_response(browser_wrapper)

            if retries < 2:
                request.user_data["retries"] = retries + 1
                Actor.log.info("Retrying {} (retry {})"
                            .format(request.url, retries + 1))
                await asyncio.sleep(0.5)
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
            browser_wrapper.exit_lock()


async def main():
    """

    """
    idle_cycles = 0
    semaphore = asyncio.Semaphore(SEMAPHORE_CONCURRENCY)

    async with Actor:
        queue = await RequestQueue.open()
        actor_input = await Actor.get_input() or {}
        start_list_url = actor_input.get('product_list_url', None)

        if start_list_url is None:
            await Actor.fail("No product list url found")

        r = Request.from_url(url=start_list_url, label="LIST")
        add_request_info = await queue.add_request(r)
        Actor.log.info(f'Seeding Queue with url: {add_request_info}')
 
        async with async_playwright() as pw:
            tasks = []
            use_res_proxies = actor_input.get("use_resedential_proxies", False)
            proxy_info = await ProxyManager.make_proxy_info(use_res_proxies)
            bp = BrowserPool(num_browsers=10, playwright=pw, 
                             proxy_info=proxy_info)
            await bp.populate()

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
                                    bp,
                                    request,
                                    semaphore)
                )
                tasks.append(task)

            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)