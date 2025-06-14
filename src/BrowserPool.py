import asyncio
from .ProxyManager import ProxyManager


class BrowserWrapper: 
    
    def __init__(self, browser, index):
        self.browser = browser
        self.index = index
        self.failure_count = 0
        self.lock = asyncio.Lock()
    
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


    @staticmethod
    async def create_browser(playwright, proxy_info):
        """

        """
        (proxy_server,
         proxy_username,
         proxy_password) = await ProxyManager.get_new_proxy(proxy_info)
        browser = await playwright.chromium.launch(headless=False)
        return browser


class BrowserPool:
    """

    """
    def __init__(self, num_browsers, playwright, proxy_info):
        self.num_browsers = num_browsers
        self.proxy_info = proxy_info
        self.playwright = playwright
        self.browser_pool = []
        self.current_index = 0

    async def populate(self):
        """
            Populate browserPool with new browser wrappers
        """
        for i in range(self.num_browsers):
            browser = await BrowserWrapper.create_browser(self.playwright, 
                                                    self.proxy_info)
            
            browser_wrapper = BrowserWrapper(browser, i)
            self.browser_pool.append(browser_wrapper)

    async def get_next_browser(self):
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
                await asyncio.sleep(1)
            else:
                if self.browser_pool[self.current_index % self.num_browsers].lock.locked():
                    self.current_index += 1
                    cur_count += 1
                else:
                    bw = self.browser_pool[self.current_index]
                    print("Returning wrapper at index: {}".format(self.current_index))
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
            # I'ts time to punish this browser
            new_browser = await BrowserWrapper.create_browser(self.playwright, 
                                                    self.proxy_info)
            
            new_browser_wrapper = BrowserWrapper(new_browser, 
                                                 browser_wrapper.index)
            self.browser_pool[browser_wrapper.index] = new_browser_wrapper
            browser_wrapper.browser.close()

            # let python deal with the garbage collection
