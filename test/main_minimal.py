from apify import Actor
from urllib.parse import urlparse
from playwright.async_api import async_playwright


async def get_new_proxy():
    proxy_info = await Actor.create_proxy_configuration(groups=["RESIDENTIAL"], 
                                                        country_code='US')
    proxy_url = await proxy_info.new_url()

    parsed = urlparse(proxy_url)

    proxy_server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
    #proxy_server = proxy_url
    proxy_username = parsed.username
    proxy_password = parsed.password

    return (proxy_server, proxy_username, proxy_password)


async def main():
    async with Actor:    
        async with async_playwright() as pw:    
            (proxy_server, proxy_username, proxy_password) = await get_new_proxy()
            browser = await pw.chromium.launch(headless=False, 
                                               proxy={"server": proxy_server, 
                                                      "username": proxy_username, 
                                                      "password": proxy_password})
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                java_script_enabled=True,
                timezone_id="America/New_York"
            )
            page = await context.new_page()
            await page.goto("https://www.amazon.com/s?k=fitness+equipment&_encoding=UTF8")