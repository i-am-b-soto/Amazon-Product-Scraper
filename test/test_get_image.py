from bs4 import BeautifulSoup
import httpx
import asyncio

async def run():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    url = "https://www.amazon.com/Zwilling-Enfingy-Electric-Programs-Cordless/dp/B08NCJ5W4P/ref=sr_1_21?_encoding=UTF8&sr=8-21"

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    img_src = None
    image_block = soup.find_all('div', class_='imgTagWrapper')
    print("Here is the image_block: {}".format(image_block))

    if image_block and len(image_block) > 0:
        img_tag = image_block[0].find('img')

        if img_tag and img_tag.has_attr('src'):
            img_src = img_tag['src']
        else:
            pass
    
    print("Here is the image: {}".format(img_src))

if __name__ == '__main__':
    asyncio.run(run())