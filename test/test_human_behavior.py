import random
import asyncio
import time
from playwright.async_api import async_playwright
from src.BrowserWrapperPool import BrowserWrapperPool
from src.browser_contexts import browser_contexts
from src.user_behavior import perform_random_user_behavior



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


async def run():
    
    async with async_playwright() as pw:
        cur_attempt = 1
        for _ in range(12):
            proxy_info = None
            bp = BrowserWrapperPool(num_browsers=10, playwright=pw, 
                                proxy_info=proxy_info, 
                                run_without_proxy=True, 
                                headless=False)
            await bp.populate()

            browser_wrapper = await bp.get_next_browser_context()
            await browser_wrapper.enter_lock()
            context = browser_wrapper.get_context()
            page = await context.new_page()
            await page.route("**/*", block_images)          
            await page.goto("https://www.amazon.com/ASTRO-Gaming-Wireless-Headset-PlayStation-Console/dp/B08DHH74JQ", timeout=12000,
                            wait_until="domcontentloaded")
            #await asyncio.sleep(3)
            start_time = time.time()
            await perform_random_user_behavior(page)
            end_time = time.time()
            print("successfully completed attempt # {} in {}".format(cur_attempt, end_time - start_time))
            cur_attempt += 1
            await page.close()
            await context.close()
            await bp.destroy()

if __name__ == "__main__":
    asyncio.run(run())
