import re
from os import environ as env
from click import group, argument, option
from time import sleep
import asyncio

from requests import get

from telegram.ext import ApplicationBuilder
from telegram.error import NetworkError

from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions, ChromeOptions
from undetected_chromedriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from .exception import CookieTimeoutException

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


def refresh_ozon_cookies(delay: float = 5):
    global OZON_COOKIE

    # profile = FirefoxProfile()
    # profile.set_preference('browser.safebrowsing.enabled', False)

    # options = FirefoxOptions()
    # options.profile = profile

    options = ChromeOptions()
    # options.browser_version = '119.0.6045.123'
    # options.add_argument('--headless')

    # driver = Firefox(options = options)
    # driver = Chrome(options = options)
    driver = Chrome(options, driver_executable_path = ChromeDriverManager().install())
    driver.get('https://www.ozon.ru/')

    sleep(delay)

    cookies = None

    for entry in driver.get_cookies():
        if cookies is None:
            cookies = f"{entry['name']}={entry['value']}"
        else:
            cookies = f"{cookies}; {entry['name']}={entry['value']}"

    driver.close()

    OZON_COOKIE = cookies


def get_ozon_price(product: str):
    if product.startswith('http'):
        url = product
    else:
        url = OZON_URL_TEMPLATE.format(product = product)

    response = get(url, headers = {'Cookie': OZON_COOKIE, 'User-Agent': USER_AGENT}, timeout = TIMEOUT)

    if response.status_code == 403:
        raise CookieTimeoutException('Cookies timed out')
    if (code := response.status_code) != 200:
        raise ValueError(f'Unknown error. Status code: {code}')

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
    refresh_ozon_cookies()

    prices = []

    token = env.get(BOT_TOKEN_ENV)
    chat = env.get(CHAT_ENV)

    if token is None:
        raise ValueError(f'Environment variable {BOT_TOKEN_ENV} must be set')

    if chat is None:
        raise ValueError(f'Environment variable {CHAT_ENV} must be set')

    # bot.add_handler(CommandHandler('t', track))

    while True:
        try:
            price, url = get_ozon_price(product)
        except CookieTimeoutException:
            refresh_ozon_cookies()
            price, url = get_ozon_price(product)

        # async def _send():
        #     app.bot.send_message(chat_id = chat, text = f'Hey! One of your products has just become cheaper. Now it costs `{int(price)}`:\n\n{url}', parse_mode = 'Markdown')

        if len(prices) > 0 and price <= prices[-1]:
            # try:
            # asyncio.run()

            app = ApplicationBuilder().token(token).build()
            asyncio.run(app.bot.send_message(chat_id = chat, text = f'Hey! One of your products has just become cheaper. Now it costs `{int(price)}`:\n\n{url}', parse_mode = 'Markdown'))

            print(prices)
            # asyncio.get_event_loop().run_in_executor(None, _send, '')

            # except NetworkError:
            #     pass

        prices.append(price)
        sleep(delay)


if __name__ == '__main__':
    main()
