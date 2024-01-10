import re
from os import environ as env
from click import group, argument, option
from time import sleep
import asyncio

from requests import get

from telegram.ext import ApplicationBuilder
from telegram.error import NetworkError

OZON_COOKIE_ENV = 'OZON_COOKIE'

OZON_COOKIE = env.get(OZON_COOKIE_ENV)

if OZON_COOKIE is None:
    raise ValueError(f'Environment variable {OZON_COOKIE_ENV} must be set')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
TIMEOUT = 3600

OZON_PRICE_REGEXP = re.compile(r'([0-9.,]+)\s₽')
OZON_URL_TEMPLATE = 'https://www.ozon.ru/product/{product}'

BOT_TOKEN_ENV = 'ZONE_BOT_TOKEN'
CHAT_ENV = 'MY_CHAT_ID'


def get_ozon_price(product: str):
    if product.startswith('http'):
        url = product
    else:
        url = OZON_URL_TEMPLATE.format(product = product)

    response = get(url, headers = {'Cookie': OZON_COOKIE, 'User-Agent': USER_AGENT}, timeout = TIMEOUT)

    print(response.status_code)

    return float(OZON_PRICE_REGEXP.search(response.text).group(1)), url


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


@main.command()
@argument('product', type = str)
@option('--delay', '-d', type = float, help = 'interval between consequitive price checks in seconds', default = 3600)
def start(product: str, delay: float):
    prices = []

    token = env.get(BOT_TOKEN_ENV)
    chat = env.get(CHAT_ENV)

    if token is None:
        raise ValueError(f'Environment variable {BOT_TOKEN_ENV} must be set')

    if chat is None:
        raise ValueError(f'Environment variable {CHAT_ENV} must be set')

    # bot.add_handler(CommandHandler('t', track))

    while True:
        price, url = get_ozon_price(product)

        # async def _send():
        #     app.bot.send_message(chat_id = chat, text = f'Hey! One of your products has just become cheaper. Now it costs `{int(price)}`:\n\n{url}', parse_mode = 'Markdown')

        if len(prices) > 0 and price <= prices[-1]:
            # try:
            # asyncio.run()

            app = ApplicationBuilder().token(token).build()
            asyncio.run(app.bot.send_message(chat_id = chat, text = f'Hey! One of your products has just become cheaper. Now it costs `{int(price)}`:\n\n{url}', parse_mode = 'Markdown'))
            # asyncio.get_event_loop().run_in_executor(None, _send, '')

            # except NetworkError:
            #     pass

        prices.append(price)
        sleep(delay)


if __name__ == '__main__':
    main()
