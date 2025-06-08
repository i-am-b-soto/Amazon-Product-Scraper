from apify import Actor
from apify.storages import Dataset, RequestQueue
from apify_client import ApifyClient
from playwright.async_api import async_playwright


SEARCH_URL = "https://www.amazon.com/s?k=gaming+headsets"


async def enqueue_listing_page(queue, url):
    await queue.add_request({
        "url": url,
        "userData": {"label": "LIST"}
    })

async def enqueue_product_page(queue, url):
    await queue.add_request({
        "url": url,
        "userData": {"label": "PRODUCT"}
    })


async def handle_list_page(page, queue):
    print("Handling list page:", page.url)

    # Get product links
    product_anchors = await page.locator('a.a-link-normal.s-no-outline').all()
    for anchor in product_anchors:
        href = await anchor.get_attribute("href")
        if href:
            await enqueue_product_page(queue, "https://www.amazon.com" + href)

    # Queue next page
    next_btn = page.locator("a.s-pagination-next")
    if await next_btn.is_visible():
        href = await next_btn.get_attribute("href")
        if href:
            await enqueue_listing_page(queue, "https://www.amazon.com" + href)


async def handle_product_page(page, dataset):
    print("Handling product page:", page.url)
    title = await page.locator("#productTitle").text_content()
    price = await page.locator(".a-price .a-offscreen").first.text_content()
    asin = page.url.split("/dp/")[-1].split("/")[0]

    await dataset.push_data({
        "url": page.url,
        "title": title.strip() if title else None,
        "price": price.strip() if price else None,
        "asin": asin,
    })


async def main():
    async with Actor:
        queue = await RequestQueue.open()
        dataset = await Dataset.open()
        await enqueue_listing_page(queue, SEARCH_URL)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context()
            while True:
                request = await queue.fetch_next_request()
                if not request:
                    break

                page = await context.new_page()
                try:
                    await page.goto(request["url"], timeout=60000)
                    label = request["userData"].get("label")
                    if label == "LIST":
                        await handle_list_page(page, queue)
                    elif label == "PRODUCT":
                        await handle_product_page(page, dataset)
                    await queue.mark_request_handled(request)
                except Exception as e:
                    print("Error:", e)
                    await queue.reclaim_request(request)
                await page.close()
            await browser.close()
