from apify import Actor
from crawlee import Request
from .product_list import get_product_urls
from .get_product import get_product
from .AmazonProduct import AmazonProduct


async def handle_product_page(page, product_url):
    """
        Handle a product page request
    """
    product = await get_product(page, product_url)
    await Actor.push_data(product.to_json())


async def handle_list_page(page, queue):
    """
        Handle a list page request
    """
    (product_urls, next_page_url) = await get_product_urls(page)
    requests = []
    for url in product_urls:
        requests.append(
            Request.from_url(url=AmazonProduct.fix_url(url), label="PRODUCT"))
    
    Actor.log.info("Adding {} urls to queue".format(len(requests)))
    await queue.add_requests_batched(requests)

    # Queue next page
    if next_page_url is not None:
        await queue.add_request(
            Request.from_url(next_page_url, label="LIST"))
    
        Actor.log.info("Adding {} to queue".format(next_page_url))