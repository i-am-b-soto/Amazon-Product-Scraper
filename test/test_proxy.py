import asyncio
from apify import Actor


async def test():
    async with Actor:
        print("inside the actor")
        proxy_info = await Actor.create_proxy_configuration(password="apify_proxy_hIqCMm9uxsg3o2TfOuBXv9fjJA95eR1LqA6v", groups=["RESIDENTIAL"], country_code='US')
        print(await proxy_info.new_url())

asyncio.run(test())