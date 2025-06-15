import asyncio
import uuid
import random
from .ProxyManager import ProxyManager
from .browser_contexts import browser_contexts


def create_session_id():
    return "session_{}".format(uuid.uuid4().hex)


class BrowserWrapper: 
    
    def __init__(self, index, session_id=None):
        self.index = index
        self.failure_count = 0
        self.lock = asyncio.Lock()
        self.session_id = session_id
    
    async def enter_lock(self):
        await self.lock.acquire()
        return self

    def exit_lock(self):
        self.lock.release()

    def get_failure_count(self):
        return self.failure_count
    
    def update_failure_count(self):
        self.failure_count += 1

    def get_browser(self):
        return self.browser
    
    def get_context(self):
        return self.context
    
    async def destroy(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def set_browser_context(self, playwright, proxy_info, no_proxy=False):
        """

        """
        if no_proxy:
            browser = await playwright.chromium.launch(headless=True)
        else:
            proxy_dict = await ProxyManager.get_new_proxy(proxy_info, 
                                                        session_id=self.session_id)
            browser = await playwright.chromium.launch(headless=True, 
                                                    proxy=proxy_dict)

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
        self.context = context
        self.browser = browser
        

class BrowserWrapperPool:
    """

    """
    def __init__(self, num_browsers, playwright, 
                 proxy_info=None, run_without_proxy=False):
        self.num_browsers = num_browsers
        self.proxy_info = proxy_info
        self.playwright = playwright
        self.browser_wrapper_pool = []
        self.current_index = 0
        self.run_without_proxy = run_without_proxy

    async def populate(self):
        """
            Populate browserPool with new browser wrappers
        """
        for i in range(self.num_browsers):
            
            bw = BrowserWrapper(index=i,
                                             session_id=create_session_id())
            await bw.set_browser_context(self.playwright,
                                                    self.proxy_info,
                                                    self.run_without_proxy)            
            self.browser_wrapper_pool.append(bw)

    async def get_next_browser_context(self):
        """
            
        """
        max_cyles = 12
        cur_cycle = 0
        cur_count = 0

        while True:
            if cur_count >= self.num_browsers:
                cur_cycle += 1
                if cur_cycle > max_cyles:
                    raise Exception("Browser Pool waited too long for an open browser")
                cur_count = 0
                await asyncio.sleep(0.5)
            
            if self.browser_wrapper_pool[self.current_index % self.num_browsers].lock.locked():
                self.current_index += 1
                cur_count += 1
            else:
                bw = self.browser_wrapper_pool[self.current_index % self.num_browsers]
                self.current_index += 1
                return bw

    async def handle_no_response(self, browser_wrapper):
        """
            Given a naughty browserWrapper that hasn't been behaving properly, 
                We need to punish it. Release the lock, and replace it! Or just mark
                it
        """
        browser_wrapper.update_failure_count()
        failure_count = browser_wrapper.get_failure_count()

        if failure_count >= 3:
            
            new_browser_wrapper = BrowserWrapper(browser_wrapper.index, 
                                                 create_session_id())
            
            # I'ts time to punish this browser
            await new_browser_wrapper.set_browser_context(self.playwright, 
                                                    self.proxy_info, 
                                                    self.run_without_proxy)

            self.browser_wrapper_pool[browser_wrapper.index] = new_browser_wrapper
            await browser_wrapper.destroy()

            # let python deal with the garbage collection
    
    async def destroy(self):
        for i in range(self.num_browsers):
            bw = self.browser_wrapper_pool[i]
            await bw.destroy()
