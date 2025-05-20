
from get_product import get_product
from get_product_urls import get_product_urls
from AmazonProduct import AmazonProduct
import json

if __name__ == "__main__":
    url = "https://www.amazon.com/ASUS-AX1800-WiFi-Router-RT-AX55/dp/B08J6CFM39/ref=pd_ci_mcx_mh_pe_im_d1_hxwPPE_sspa_dk_det_cao_p_20_1"
    #scrape_amazon_product(url)
    #scrape_amazon_product_selenium(url)
    #list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=keyboard")
    #list_of_product_urls = scrape_list("https://www.amazon.com/s?i=luxury&bbn=20657941011&rh=n%3A18981045011%2Cn%3A20657941011%2Cn%3A20657942011&dc&ds=v1%3AI9u5X8yPzX391p21IhAFtYZdUDUUms%2Fh0KIYANVj24Y&_encoding=UTF8&_encoding=UTF8")
    #list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=Shoes&rh=p_36%3A-5000&_encoding=UTF8")
    
    """
    with open("dummy/test-product-urls.txt", "w") as f:
        for url in list_of_product_urls:
            full_url = "https://www.amazon.com{url}\n".format(url=url)
            f.write(full_url)
    
            
    """
    product_urls = []

    with open("dummy/test-product-urls.txt", "r") as f:
        for url in f:
            product_urls.append(url)

    with open("dummy/products.txt", "w") as f:
        for url in product_urls:
            try:
                p = get_product(url)
            except Exception as e:
                print("failure to get url at: {}\n{}".format(url, e))
            else:
                print(json.dumps(p.to_json()))
                f.write(json.dumps(p.to_json()))

    p = get_product("https://www.amazon.com/Skechers-Expected-Avillo-Relaxed-Fit-Loafer/dp/B00MU2OR3W/ref=sr_1_23?_encoding=UTF8&dib=eyJ2IjoiMSJ9.GCX-gmUPY34FyIrVRapuxKCB_e8lxR1XeDRDNZTawbwvK0lmL7rLZxlKar9loBfBaqi-Bev6GLINCB0_IR1ZP6Bjhcq7qtuDkscNqpStMfl8ZgXeoUOXSCw-iod0nw8cI2Lhqp-6lrg3TgwnSKWsNMpQVb1yD413php1x-KQXJvIPFTiDJ6zSDilx6IeBSnNfnLfhNHCPBZI5mBYUZ_FeMiEw6fJrVTv4vdCytZAw97LZkI5TMuyEdLsWN53KINW1CbfORTcdSmHzyronmUx4OO9dFqJbyseAFj3tdxT70Y.Ea2uK9uO0aGVka39Ihdx4x2BywSEujefTob_asA9Vsk&dib_tag=se&keywords=Shoes&qid=1747721061&refinements=p_36%3A-5000&sr=8-23")
    print(json.dumps(p.to_json()))
    
