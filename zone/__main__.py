from time import sleep
from click import group, argument, option
from datetime import datetime
from threading import Thread
import asyncio

from .OzonParser import OzonParser
from .Tracker import Tracker
from .TelegramBot import TelegramBot


NEWLINE = '\n'

PRODUCT = 'product'


@group()
def main():
    pass


@main.command()
@argument('product', type = str)
def parse(product: str):
    tracker = Tracker(products = [product])
    parser = OzonParser(tracker = tracker)

    parser.push_prices(datetime.now(), check_targets = False)

    print(f'The product costs {tuple(tracker.prices[product].values())[-1]}')


def _start_bot(tracker: Tracker, delay: float):
    parser = OzonParser(tracker = tracker)

    while True:
        timestamp = datetime.now()
        parser.push_prices(timestamp)

        tracker.save()

        sleep(delay)

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    # TelegramBot(tracker).poll()


@main.command()
@argument('path', type = str, default = 'assets/products.txt')
@option('--delay', '-d', type = float, help = 'interval between consequitive price checks in seconds', default = 3600)
def start(path: str, delay: float):
    tracker = Tracker(path)

    bot_thread = Thread(target = _start_bot, args = (tracker, delay))
    bot_thread.start()

    TelegramBot(tracker).poll()


if __name__ == '__main__':
    main()
