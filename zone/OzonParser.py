import re

from requests import Response

from .Parser import Parser
from .exception import CookieTimeoutException


ROOT = 'https://www.ozon.ru'
PRICE_REGEXP = re.compile(r'([0-9.,]+)\s₽')


class OzonParser(Parser):
    root = ROOT
    product_url = f'{ROOT}/product/{{product}}'

    def __init__(self):
        super().__init__()

    def extract_price(self, response: Response):
        if response.status_code == 403:
            raise CookieTimeoutException('Cookies timed out')
        if (code := response.status_code) != 200:
            raise ValueError(f'Unknown error. Status code: {code}')

        return float(PRICE_REGEXP.search(response.text).group(1))
