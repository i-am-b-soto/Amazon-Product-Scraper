from apify import Actor
import httpx
import asyncio
import random
import uuid
import json

from src.ProxyManager import ProxyManager
from src.browser_contexts import browser_contexts


async def test():
    async with Actor:    
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

        proxy_info = await Actor.create_proxy_configuration(groups=["StaticUS3"])
        
        ip_dict = {}
        unique_ips = 0
        proxy_url = await proxy_info.new_url(session_id=uuid.uuid4().hex)
        for _ in range(30):
            
            async with httpx.AsyncClient(headers=headers, 
                                        proxy=proxy_url, 
                                    timeout=6, 
                                    follow_redirects=True) as client:
            
                response = await client.get("https://httpbin.org/ip", timeout=6000,
                                headers=headers) 
                
                try:
                    ip_json = json.loads(response.text)
                    ip = ip_json["origin"]
                    print("ip: {} - session_id: {}".format(ip, proxy_url))
                    print(ip)
                    if ip in ip_dict:
                        print("{} already in ip dict. with url: {}".format(ip, proxy_url))
                        
                    else:
                        unique_ips += 1
                        print("new ip, unique total = {}".format(unique_ips))
                        ip_dict[ip] = True
                        
                except json.decoder.JSONDecodeError as e:
                    continue

asyncio.run(test())