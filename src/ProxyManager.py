from apify import Actor
from urllib.parse import urlparse


class ProxyManager:
    @staticmethod
    async def make_residential_proxy_info():
        #proxy_info = await Actor.create_proxy_configuration(
        #            groups=["RESIDENTIAL"], country_code='US')
        proxy_info = await Actor.create_proxy_configuration(country_code='US')
        
        return proxy_info

    @staticmethod
    async def get_new_proxy(proxy_info):
        """
            return dict
        """
        proxy_url = await proxy_info.new_url()
        parsed = urlparse(proxy_url)
        return {
            "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            "username": parsed.username,
            "password": parsed.password,
        }