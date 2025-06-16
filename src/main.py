import asyncio
import httpx
import random
import time
import ssl
import uuid
from itertools import cycle
from apify import Actor
from crawlee import Request
from apify.storages import RequestQueue
from .browser_contexts import browser_contexts
from .custom_exceptions import ProductListPageNotLoaded, ProductNotLoaded
from .request_handlers import handle_product_page, handle_list_page


SEMAPHORE_CONCURRENCY = 12
NUM_BROWSERS = 4
MAX_IDLE_CYCLES = 100
REQUEST_TIMEOUT = 6000
BANNED_DOMAINS = ["media-amazon.com", "ssl-images-amazon.com", 
                  "amazon-adsystem.com"]



class SessionManager:
    def __init__(self, proxy_info):
        self._proxy_info = proxy_info
        self._failure_count = 0
        self._session_id=SessionManager.get_new_session_id()


    @staticmethod
    def get_new_session_id():
        return "session_{}".format(uuid.uuid4().hex)


    async def get_proxy_url(self):
        url = await self._proxy_info.new_url(session_id=self._session_id)
        return url
    

    async def handle_failure(self):
        self._failure += 1
        if self._failure > 3:
            self._session_id=SessionManager.get_new_session_id()



async def make_request(url, proxy_url, referer=None):
    context = random.choice(browser_contexts)

    # Extract data from the context
    user_agent = context["user_agent"]
    locale = context["locale"]
    viewport_width = str(context["viewport"]["width"])

    headers = {
        "User-Agent":  user_agent,
        "Accept-Language": locale,
        "Viewport-Width": viewport_width
    }
    if referer is not None:
        headers["Referer"] = referer

    async with httpx.AsyncClient(headers=headers, 
                                 proxy=proxy_url, 
                                 timeout=6, 
                                follow_redirects=True) as client:
        response = await client.get(url)
    
    return response


async def process_request(queue, request_info, sm, semaphore):
    """
        Process a request from the queue
    """
    async with semaphore:
        #proxy_url = await pm.get_proxy_url()
        try:
            start_time = time.time()
            proxy_url = await sm.get_proxy_url()
            response = await make_request(request_info.url, proxy_url, 
                                          request_info.user_data.get("referer", None))
            end_time = time.time()
            print("Request took {}s".format(end_time - start_time))

            label = request_info.label
            if label == "LIST":
                await handle_list_page(response, queue)

            elif label == "PRODUCT":
                await handle_product_page(response, request_info.url)
            
            await queue.mark_request_as_handled(request_info)
            Actor.log.info("✅ Successfully processed request: {}"
                        .format(request_info.url))

        except (httpx.TimeoutException, 
                ProductNotLoaded,
                ssl.SSLError,
                ProductListPageNotLoaded) as e:
            retries = request_info.user_data.get("retries", 0)
            Actor.log.warning("Timeout for url {} (attempt {}): {}\n"
                            .format(request_info.url, retries + 1, e))
            
            await sm.handle_failure()

            if retries < 2:
                request_info.user_data["retries"] = retries + 1
                await queue.reclaim_request(request_info, forefront=False)
            
            else:
                await queue.mark_request_as_handled(request_info)
                Actor.log.error("❌ Failed permanently: {} after {} attempts"
                                .format(request_info.url, retries + 1))
                
        except Exception as e:
            # All other errors will fall under here
            await queue.mark_request_as_handled(request_info) # Don't bother with a re-try
            Actor.log.error("❌ Failed permanently: {} {}"
                            .format(request_info.url, e))


async def main():
    """

    """
    async with Actor:
        idle_cycles = 0

        queue = await RequestQueue.open()
        actor_input = await Actor.get_input() or {}

        start_list_url = actor_input.get('product_list_url', None)

        use_resedential_proxies = actor_input.get('use_resedential_proxies', False)

        semaphore_count = actor_input.get('parallel_worker_count', 12)

        request_timeout = actor_input.get('request_timeout')

        global REQUEST_TIMEOUT
        REQUEST_TIMEOUT = request_timeout

        semaphore = asyncio.Semaphore(semaphore_count)

        if start_list_url is None:
            await Actor.fail("No product list url found")

        r = Request.from_url(url=start_list_url, label="LIST")
        add_request_info = await queue.add_request(r)
        Actor.log.info(f'Seeding Queue with url: {add_request_info}')
 
        tasks = []
        proxy_info = None
        if use_resedential_proxies:
            proxy_info = await Actor.create_proxy_configuration(
                        groups=["RESIDENTIAL"], country_code='US')
        else:
            proxy_info = await Actor.create_proxy_configuration(groups=["StaticUS3"], country_code='US')
        
        sm = SessionManager(proxy_info)
        while not await queue.is_finished():
            request_info = await queue.fetch_next_request()
            if request_info is None:
                idle_cycles += 1
                
                if idle_cycles >= MAX_IDLE_CYCLES:
                    Actor.log.warning("Queue idle too long. Exiting")
                    break

                await asyncio.sleep(3)
                continue
            else:
                idle_cycles = 0
            
            task = asyncio.create_task(
                process_request(queue,
                                request_info,
                                sm,
                                semaphore)
            )
            tasks.append(task)

        # Wait for any remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
            