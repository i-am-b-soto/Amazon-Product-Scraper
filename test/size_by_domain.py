import asyncio
from urllib.parse import urlparse
from collections import defaultdict

from playwright.async_api import async_playwright

banned_domains = ["m.media-amazon.com", "images-na.ssl-images-amazon.com"]


async def block_images(route, request):
    if route.request.resource_type == "image":
        print(f"Blocking image: {route.request.url}")
        await route.abort()
    else:
        l = False
        for domain in banned_domains:
            if request.url.find(domain) != -1:
                await route.abort()
                l = True
        else:
            if not l:
                await route.continue_()


async def monitor_domain_downloads(url):
    domain_totals = defaultdict(int)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
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

        async def handle_response(response):
            try:
                if response.request.method != "GET":
                    return
                
                status = response.status
                if 300 <= status < 400:
                    # Redirect — no body available
                    return
                if status == 204:
                    # No content
                    return
                if status >= 400:
                    # Client/server error
                    print(f"Error response ({status}): {response.url}")
                    return    

                parsed_url = urlparse(response.url)
                domain = parsed_url.netloc

                headers = response.headers
                content_length = headers.get("content-length")

                if content_length:
                    size_bytes = int(content_length)
                else:
                    body = await response.body()
                    size_bytes = len(body)

                domain_totals[domain] += size_bytes

            except Exception as e:
                print(f"Error reading response from {response.url}: {e}")

        page.on("response", handle_response)

        print(f"Loading {url} ...")
        await page.goto(url, wait_until="domcontentloaded")

        await browser.close()

        print("\nDownload summary by domain:")
        total_all = 0
        for domain, size in sorted(domain_totals.items(), key=lambda x: -x[1]):
            size_mb = size / (1024 ** 2)
            total_all += size
            print(f"{domain:<40} {size_mb:.2f} MB")

        print(f"\nTotal downloaded: {total_all / (1024 ** 3):.2f} GB")


async def monitor_domain_downloads_no_images(url):
    domain_totals = defaultdict(int)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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

        async def handle_response(response):
            try:
                if response.request.method != "GET":
                    return
                
                # Skip redirects (no meaningful body)
                if 300 <= response.status < 400:
                    return                

                parsed_url = urlparse(response.url)
                domain = parsed_url.netloc

                headers = response.headers
                content_length = headers.get("content-length")

                if content_length:
                    size_bytes = int(content_length)
                else:
                    body = await response.body()
                    size_bytes = len(body)

                domain_totals[domain] += size_bytes

            except Exception as e:
                print(f"Error reading response from {response.url}: {e}")

        page.on("response", handle_response)

        print(f"Loading {url} ...")
        await page.route("**/*", block_images)
        await page.goto(url, wait_until="domcontentloaded")

        await browser.close()

        print("\nDownload summary by domain:")
        total_all = 0
        for domain, size in sorted(domain_totals.items(), key=lambda x: -x[1]):
            size_mb = size / (1024 ** 2)
            total_all += size
            print(f"{domain:<40} {size_mb:.2f} MB")

        print(f"\nTotal downloaded: {total_all / (1024 ** 3):.2f} GB")



async def analyze_no_images(url):
    domain_totals = defaultdict(int)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
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


        async def handle_response(response):
            try:
                if response.request.method != "GET":
                    return

                if 300 <= response.status < 400 or response.status == 204:
                    return

                resource_type = response.request.resource_type  # e.g., "image", "script", "xhr", etc.

                headers = response.headers
                content_length = headers.get("content-length")

                if content_length:
                    size_bytes = int(content_length)
                else:
                    try:
                        body = await response.body()
                        size_bytes = len(body)
                    except:
                        return

                resource_type_totals[resource_type] += size_bytes

            except Exception as e:
                print(f"Error on {response.url}: {e}")

        page.on("response", handle_response)

        print(f"Loading {url} ...")
        await page.route("**/*", lambda route: 
            route.abort() if route.request.resource_type == "image" else route.continue_()
        )
        await page.goto(url, wait_until="domcontentloaded")

        await browser.close()

        print("\nDownload summary by domain:")
        total_all = 0
        for domain, size in sorted(domain_totals.items(), key=lambda x: -x[1]):
            size_mb = size / (1024 ** 2)
            total_all += size
            print(f"{domain:<40} {size_mb:.2f} MB")

        print(f"\nTotal downloaded: {total_all / (1024 ** 3):.2f} GB")


if __name__ == '__main__':
    # Example usage
    """
        asyncio.run(monitor_domain_downloads("https://www.amazon.com/s?k=cooker&_encoding=UTF8"))

        images-na.ssl-images-amazon.com          1.61 MB
        www.amazon.com                           0.80 MB
        m.media-amazon.com                       0.39 MB
        fls-na.amazon.com                        0.00 MB
    """
    """
        asyncio.run(monitor_domain_downloads("https://www.amazon.com/SteelSeries-Multi-System-Headset-Lightweight-Noise-Cancelling/dp/B0BQ8XTJG3"))

        m.media-amazon.com                       2.25 MB
        www.amazon.com                           1.85 MB
        images-na.ssl-images-amazon.com          0.68 MB
        aax-us-iad.amazon.com                    0.00 MB
        fls-na.amazon.com                        0.00 MB        
    """

    """
        asyncio.run(monitor_domain_downloads_no_images("https://www.amazon.com/SteelSeries-Multi-System-Headset-Lightweight-Noise-Cancelling/dp/B0BQ8XTJG3"))    
        Download summary by domain:
        m.media-amazon.com                       6.91 MB
        www.amazon.com                           1.85 MB
        images-na.ssl-images-amazon.com          0.63 MB
        aax-us-iad.amazon.com                    0.00 MB
        fls-na.amazon.com                        0.00 MB    
    """
    #asyncio.run(monitor_domain_downloads_no_images("https://www.amazon.com/SteelSeries-Multi-System-Headset-Lightweight-Noise-Cancelling/dp/B0BQ8XTJG3")) 


    asyncio.run(monitor_domain_downloads_no_images("https://www.amazon.com/SteelSeries-Multi-System-Headset-Lightweight-Noise-Cancelling/dp/B0BQ8XTJG3"))