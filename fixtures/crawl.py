import json
import logging

import requests
from bs4 import BeautifulSoup

# configure logging
logging.basicConfig(format="%(asctime)s : %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def scrap_data():
    products = []

    for i in range(21):
        if i == 0 or i == 1:
            url = "https://shop.rangechem.co.ke/home-1/shop/"
        else:
            url = f"https://shop.rangechem.co.ke/home-1/shop/{i}"

        response = requests.get(url)

        if not response.ok:
            logger.error(f"Failed to scrap {url} : {response.text}")

        soup = BeautifulSoup(response.text, "html.parser")
        main_div = soup.find("div", {"class": "columns-6"})

        products_ul_list = main_div.find("ul", {"class": "products columns-6"})

        for li in products_ul_list.find_all("li"):
            title = li.find("h3", {"class": "woocommerce-loop-product__title"}).text
            image = li.find(
                "img", {"class": "attachment-shop_catalog size-shop_catalog"}
            )["data-src"]
            price = li.find("span", {"class": "woocommerce-Price-amount amount"}).text
            products.append(
                {"name": title, "image": image, "price": price.replace(price[:3], "")}
            )

    if len(products):
        with open("data.json", "w") as file:
            dump = json.dumps(products)
            file.write(dump)
        file.close()

        logger.info("The END!")


scrap_data()
