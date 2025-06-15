import asyncio
from apify import Actor
from urllib.parse import urlparse
from playwright.async_api import async_playwright



async def main():
    async with Actor:    
        async with async_playwright() as pw:    

            browser = await pw.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900},
                locale="en-US",
                java_script_enabled=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.google.com/"
                }               
            )
            page = await context.new_page()
            await page.goto("https://www.amazon.com/s?k=fitness+equipment&_encoding=UTF8")
            await asyncio.sleep(6)