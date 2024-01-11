from os import environ as env
from abc import ABC, abstractmethod
from time import sleep
import asyncio
from datetime import datetime

from requests import get, Response
from selenium.webdriver import ChromeOptions
from undetected_chromedriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager

from telegram.ext import ApplicationBuilder

from .exception import CookieTimeoutException
from .Tracker import Tracker


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
TIMEOUT = 3600

BOT_TOKEN_ENV = 'ZONE_BOT_TOKEN'
CHAT_ENV = 'MY_CHAT_ID'


class Parser(ABC):
    root = None
    product_url = None

    def __init__(self, tracker: Tracker, cookies: str = None, cookies_check_delay: float = 5):
        self.tracker = tracker

        self.cookies = cookies
        self.cookies_check_delay = cookies_check_delay

        self.token = token = env.get(BOT_TOKEN_ENV)
        self.chat = chat = env.get(CHAT_ENV)

        if token is None:
            raise ValueError(f'Environment variable {BOT_TOKEN_ENV} must be set')

        if chat is None:
            raise ValueError(f'Environment variable {CHAT_ENV} must be set')

    def _refresh_cookies(self):
        options = ChromeOptions()

        driver = Chrome(options, driver_executable_path = ChromeDriverManager().install())
        driver.get(self.root)

        sleep(self.cookies_check_delay)

        cookies = None

        for entry in driver.get_cookies():
            if cookies is None:
                cookies = f"{entry['name']}={entry['value']}"
            else:
                cookies = f"{cookies}; {entry['name']}={entry['value']}"

        driver.close()

        self.cookies = cookies

    def get_price(self, product: str):
        if product.startswith('http'):
            url = product
        else:
            url = self.product_url.format(product = product)

        # print(url)

        response = get(url, headers = {'Cookie': self.cookies, 'User-Agent': USER_AGENT}, timeout = TIMEOUT)

        return self.extract_price(response), url

    def push_prices(self, timestamp: datetime, check_targets: bool = True):
        if self.cookies is None:
            self._refresh_cookies()

        for product in self.tracker.products:
            if check_targets and not self.is_target_parser_of(product):
                continue

            try:
                price, url = self.get_price(product)
            except CookieTimeoutException:
                self._refresh_cookies()
                price, url = self.get_price(product)

            prices = tuple(self.tracker.prices[product].values())

            if len(prices) > 0 and price <= prices[-1]:
                app = ApplicationBuilder().token(self.token).build()
                asyncio.run(app.bot.send_message(chat_id = self.chat, text = f'Hey! One of your products has just become cheaper. Now it costs `{int(price)}`:\n\n{url}', parse_mode = 'Markdown'))

            self.tracker.push(product, price, timestamp)

    @abstractmethod
    def extract_price(self, response: Response):
        pass

    @abstractmethod
    def is_target_parser_of(self, product: str):
        pass
