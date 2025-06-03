from src.get_product import get_product
from src.selenium_adapter import get_driver
import json

"""
    Some URLS we can try: 
        https://www.amazon.com/BYYBUO-SmartPad-A10-Quad-Core-Touchscreen/dp/B09TQYQL1Z/ref=sr_1_18?_encoding=UTF8&sr=8-18&xpid=9i2Q1Jj8Hn_Sy
"""

if __name__ == '__main__':
    driver = get_driver()
    product = get_product("https://www.amazon.com/BYYBUO-SmartPad-A10-Quad-Core-Touchscreen/dp/B09TQYQL1Z/ref=sr_1_18?_encoding=UTF8&sr=8-18&xpid=9i2Q1Jj8Hn_Sy", driver)
    print(json.dumps(product.to_json()))
