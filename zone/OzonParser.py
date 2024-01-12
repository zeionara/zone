import re

from requests import Response

from .Parser import Parser
from .exception import CookieTimeoutException


ROOT = 'https://www.ozon.ru'
# PRICE_BLOCK_REGEXP = re.compile(r'border-radius:8px.+[0-9., ]+\s₽')
# PRICE_BLOCK_REGEXP = re.compile(r'webSale.+border-radius:8px.+[0-9., ]+\s₽')
# PRICE_BLOCK_REGEXP = re.compile(r'c Ozon Картой.+>+[0-9., ]+\s₽')
PRICE_REGEXP = re.compile(r'([0-9., ]+)\s₽.+c Ozon Картой')


class OzonParser(Parser):
    root = ROOT
    product_url = f'{ROOT}/product/{{product}}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extract_price(self, response: Response):
        # print(response.status_code)

        if response.status_code == 403:
            raise CookieTimeoutException('Cookies timed out')
        if (code := response.status_code) != 200:
            raise ValueError(f'Unknown error. Status code: {code}')

        # price_block = PRICE_BLOCK_REGEXP.search(response.text).string

        # with open('response.html', 'w') as file:
        #     file.write(response.text)

        # for match in PRICE_BLOCK_REGEXP.findall(response.text):
        #     print(match)

        # dd

        # print(price_block)

        return float(PRICE_REGEXP.search(response.text).group(1).replace(' ', ''))

    def is_target_parser_of(self, product: str):
        if product.startswith('http'):
            return 'ozon.ru' in product

        raise ValueError(f'Target platform of product {product} cannot be established')
