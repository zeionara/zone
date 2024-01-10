import re
from os import environ as env
from click import group, argument

from requests import get

OZON_COOKIE_ENV = 'OZON_COOKIE'

OZON_COOKIE = env.get(OZON_COOKIE_ENV)

if OZON_COOKIE is None:
    raise ValueError(f'Environment variable {OZON_COOKIE_ENV} must be set')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
TIMEOUT = 3600

OZON_PRICE_REGEXP = re.compile(r'([0-9.,]+)\s₽')
OZON_URL_TEMPLATE = 'https://www.ozon.ru/product/{product}'


def get_ozon_price(product: str):
    url = OZON_URL_TEMPLATE.format(product = product)

    response = get(url, headers = {'Cookie': OZON_COOKIE, 'User-Agent': USER_AGENT}, timeout = TIMEOUT)

    return float(OZON_PRICE_REGEXP.search(response.text).group(1))


@group()
def main():
    pass


@main.command()
@argument('product', type = str)
def parse(product: str):
    price = get_ozon_price(product)

    print(f'The product costs {price}')

    # for match in OZON_PRICE_REGEXP.findall(response.text):
    #     print(match)

    # print(response.status_code)
    # print(response.content)


if __name__ == '__main__':
    main()
