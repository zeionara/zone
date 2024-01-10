import re

from requests import Response

from .Parser import Parser
from .exception import CookieTimeoutException


ROOT = 'https://www.ozon.ru'
PRICE_REGEXP = re.compile(r'([0-9., ]+)\s₽')


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

        return float(PRICE_REGEXP.search(response.text).group(1).replace(' ', ''))

    def is_target_parser_of(self, product: str):
        if product.startswith('http'):
            return 'ozon.ru' in product

        raise ValueError(f'Target platform of product {product} cannot be established')
