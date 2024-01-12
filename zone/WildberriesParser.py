import re

from requests import Response

from .Parser import Parser


ROOT = 'https://www.wildberries.ru'
PRICE_REGEXP = re.compile(r'final_price">\s*([0-9., ]+)\s₽')


class WildberriesParser(Parser):
    root = ROOT
    product_url = f'{ROOT}/catalog/{{product}}/details.aspx'
    card_url = 'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&spp=29&nm={product}'

    requires_cookies = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_request_url(self, url: str):
        return self.card_url.format(product = url[::-1].split('/', maxsplit = 2)[1][::-1])

    def extract_price(self, response: Response):
        # print(response.status_code)

        # if response.status_code == 403:
        #     raise CookieTimeoutException('Cookies timed out')

        if (code := response.status_code) != 200:
            raise ValueError(f'Unknown error. Status code: {code}')

        # with open('response-wb.html', 'w') as file:
        #     file.write(response.text)

        return response.json()['data']['products'][0]['salePriceU'] / 100

    def is_target_parser_of(self, product: str, suppress_errors: bool = False):
        if product.startswith('http'):
            return 'wildberries.ru' in product

        if suppress_errors:
            return False
        raise ValueError(f'Target platform of product {product} cannot be established')
