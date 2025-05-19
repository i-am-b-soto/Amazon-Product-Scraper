
from get_product_urls import get_product_urls

if __name__ == "__main__":
    url = "https://www.amazon.com/ASUS-AX1800-WiFi-Router-RT-AX55/dp/B08J6CFM39/ref=pd_ci_mcx_mh_pe_im_d1_hxwPPE_sspa_dk_det_cao_p_20_1"
    #scrape_amazon_product(url)
    #scrape_amazon_product_selenium(url)
    #list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=keyboard")
    #list_of_product_urls = scrape_list("https://www.amazon.com/s?i=luxury&bbn=20657941011&rh=n%3A18981045011%2Cn%3A20657941011%2Cn%3A20657942011&dc&ds=v1%3AI9u5X8yPzX391p21IhAFtYZdUDUUms%2Fh0KIYANVj24Y&_encoding=UTF8&_encoding=UTF8")
    list_of_product_urls = get_product_urls("https://www.amazon.com/s?k=Shoes&rh=p_36%3A-5000&_encoding=UTF8")

    with open("dummy/test-results.txt", "w") as f:
        for url in list_of_product_urls:
            f.write("https://www.amazon.com{url}\n".format(url=url))

    