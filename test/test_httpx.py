import time
import httpx
import asyncio


async def fetch_product_list():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    url = "https://www.amazon.com/s?k=headphones"

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        response = await client.get(url)

    print(response.status_code)
    with open("httpx_test.html", "w") as f:
        f.write(response.text)
    #print(response.text[:1000])

async def fetch_product():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    urls = ["https://www.amazon.com/Hamilton-Beach-72850-Processor-Electric/dp/B06Y2GZWCJ/ref=sr_1_4?_encoding=UTF8&s=kitchen-intl-ship&sr=1-4",
            "https://www.amazon.com/Pack-Kitchen-Dishcloths-Absorbent-Multicolor/dp/B08C2H9CSQ/ref=sr_1_10?_encoding=UTF8&s=kitchen-intl-ship&sr=1-10",
            "https://www.amazon.com/Leaflai-Oil-Dispenser-Bottle-Kitchen/dp/B0BC34MQKZ/ref=sr_1_13?_encoding=UTF8&s=kitchen-intl-ship&sr=1-13",
            "https://www.amazon.com/Toaster-Fits-anywhereTM-Kitchenware-Setting-Removable/dp/B0CYJBB2JQ/ref=sr_1_14?_encoding=UTF8&s=kitchen-intl-ship&sr=1-14",
            "https://www.amazon.com/NINESTARS-DZT-50-28-Automatic-Touchless-Rectangular/dp/B06ZYKBF2Z/ref=sr_1_18?_encoding=UTF8&s=kitchen-intl-ship&sr=1-18",
            "https://www.amazon.com/Pyrex-Sculpted-BPA-Free-Nesting-Prepping/dp/B0BWL3VH3Y/ref=sr_1_52?_encoding=UTF8&sr=8-52&xpid=88Fjo-cBkfsVu",
            "https://www.amazon.com/KOHLER-R22867-SD-VS-Pulldown-Kitchen-Stainless/dp/B09RCCPTX2/ref=sr_1_73?_encoding=UTF8&sr=8-73&xpid=88Fjo-cBkfsVu",
            "https://www.amazon.com/An-Elephant-in-My-Kitchen-audiobook/dp/B07Z5CKRVG/ref=sr_1_85?_encoding=UTF8&sr=8-85&xpid=88Fjo-cBkfsVu",
            "https://www.amazon.com/Moen-3942SRS-Kitchen-Dispenser-Stainless/dp/B0087R52DI/ref=sr_1_98?_encoding=UTF8&sr=8-98&xpid=88Fjo-cBkfsVu"
            ]

    for url in urls:
        start_time = time.time()
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            await client.get(url)
            
        end_time = time.time()
        print("Response took {} seconds".format(end_time - start_time))
        

    """
    print(response.status_code)
    with open("httpx_test_product.html", "w") as f:
        f.write(response.text)
    """

if __name__ == '__main__':
    asyncio.run(fetch_product())