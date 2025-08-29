from apify import Actor
import asyncio
import random

from src.ProxyManager import ProxyManager
from playwright.async_api import async_playwright
from src.browser_contexts import browser_contexts


async def test():
    async with Actor:    
        async with async_playwright() as pw:
            for _ in range(5):
                proxy_info = await ProxyManager.make_proxy_info(True)
                proxy_stats = await ProxyManager.get_new_proxy(proxy_info)

                browser = await pw.chromium.launch(headless=True, 
                                                        proxy=proxy_stats)
                
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
                
                await page.goto("https://httpbin.org/ip", timeout=6000,
                                wait_until="domcontentloaded") 
                
                content = await page.content()
                print(content)

                page.close()
                context.close()
                browser.close()
    
asyncio.run(test())