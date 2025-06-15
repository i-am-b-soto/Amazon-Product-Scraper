import random
import asyncio
import time
from playwright.async_api import async_playwright
from src.ProxyManager import ProxyManager
from src.BrowserPool import BrowserPool
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
            bp = BrowserPool(num_browsers=10, playwright=pw, 
                                proxy_info=proxy_info, run_without_proxy=True)
            await bp.populate()

            
            browser_wrapper = await bp.get_next_browser()
            await browser_wrapper.enter_lock()
            browser = browser_wrapper.get_browser()
            print("browser: {}".format(browser))
            context_config = random.choice(browser_contexts)
            context = await browser.new_context(
                user_agent=context_config["user_agent"],
                locale=context_config["locale"],
                viewport=context_config["viewport"],
                is_mobile=False,
                java_script_enabled=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )
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
