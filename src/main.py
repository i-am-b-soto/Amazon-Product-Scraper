import asyncio
from apify import Actor
from crawlee import Request
from apify.storages import RequestQueue
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError, Error as playwright_error

from .request_handlers import handle_product_page, handle_list_page
from .ProxyManager import ProxyManager
from .BrowserWrapperPool import BrowserWrapperPool
from .custom_exceptions import ProductListPageNotLoaded, ProductNotLoaded



SEMAPHORE_CONCURRENCY = 3
NUM_BROWSERS = 4
MAX_IDLE_CYCLES = 240
REQUEST_TIMEOUT = 18000
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


async def process_request(queue, bwp, request, semaphore, add_human_behavior):
    """
        Process a request from the queue
    """
    async with semaphore:
        bw = await bwp.get_next_browser_context()
        context = bw.get_context() 
        page = await context.new_page()

        try:
            await page.route("**/*", block_images)          
            await page.goto(request.url, wait_until="domcontentloaded", 
                            timeout=20000)
            label = request.label
            if label == "LIST":
                await handle_list_page(page, queue, add_human_behavior)

            elif label == "PRODUCT":
                await handle_product_page(page, request.url, 
                                          add_human_behavior)
            
            await queue.mark_request_as_handled(request)
            Actor.log.info("✅ Successfully processed request: {}"
                        .format(request.url))

        except (TimeoutError, playwright_error, 
                ProductListPageNotLoaded, ProductNotLoaded) as e:
            # Catch Timeout Errors
            retries = request.user_data.get("retries", 0)
            Actor.log.warning("Error on {} (attempt {}): {}"
                            .format(request.url, retries + 1, e))
            
            await bwp.handle_no_response(bw)

            if retries < 2:
                request.user_data["retries"] = retries + 1
                await queue.reclaim_request(request, forefront=False)
            
            else:
                await queue.mark_request_as_handled(request)
                Actor.log.error("❌ Failed permanently: {} after {} attempts"
                                .format(request.url, retries + 1))
            #content = await page.content
            #dataset.push({"example": content})

        except Exception as e:
            # All other errors will fall under here
            await queue.mark_request_as_handled(request) # Don't bother with a re-try
            Actor.log.error("❌ Failed permanently: {} {}"
                            .format(request.url, e))            

        finally:
            await page.close()


async def main():
    """

    """
    async with Actor:
        idle_cycles = 0

        queue = await RequestQueue.open()
        actor_input = await Actor.get_input() or {}

        start_list_url = actor_input.get('product_list_url', None)
        #advanced_input = actor_input.get('advanced')

        semaphore_count = actor_input.get('parallel_worker_count', 5)
        browser_context_count = actor_input.get('browser_context_count', 5)

        add_human_behvaior = actor_input.get('add_human_behavior', False)
        headless = actor_input.get("headless", True)
        request_timeout = actor_input.get('request_timeout')

        global REQUEST_TIMEOUT
        REQUEST_TIMEOUT = request_timeout

        semaphore = asyncio.Semaphore(semaphore_count)

        # Save a named dataset to a variable
        bad_html = await Actor.open_dataset(name='bad-html')

        if start_list_url is None:
            await Actor.fail("No product list url found")

        """
        if browser_context_count < semaphore_count:
            await Actor.fail("Number of browser contexts should not be less " \
            "than number of parallel workers")
        """

        r = Request.from_url(url=start_list_url, label="LIST")
        add_request_info = await queue.add_request(r)
        Actor.log.info(f'Seeding Queue with url: {add_request_info}')
 
        async with async_playwright() as pw:
            tasks = []
            use_res_proxies = actor_input.get("use_resedential_proxies", False)
            proxy_info = await ProxyManager.make_proxy_info(use_res_proxies)
            bwp = BrowserWrapperPool(num_browsers=browser_context_count, 
                                     playwright=pw, 
                                     proxy_info=proxy_info,
                                     headless=headless
                                     )
            await bwp.populate()

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
                                    bwp,
                                    request,
                                    semaphore,
                                    add_human_behvaior)
                )
                tasks.append(task)

            # Wait for any remaining tasks
            if tasks:
                await asyncio.gather(*tasks)
            
            await bwp.destroy()