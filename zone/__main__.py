from time import sleep
from click import group, argument, option
from datetime import datetime
from threading import Thread
import asyncio

from .OzonParser import OzonParser
from .WildberriesParser import WildberriesParser
from .Tracker import Tracker, UserTracker
from .TelegramBot import TelegramBot


NEWLINE = '\n'

PRODUCT = 'product'


@group()
def main():
    pass


@main.command()
@argument('product', type = str)
def parse(product: str):
    tracker = UserTracker(products = [product])

    ozon_parser = OzonParser(tracker = tracker)
    wildberries_parser = WildberriesParser(tracker = tracker)

    if wildberries_parser.is_target_parser_of(product, suppress_errors = True):
        wildberries_parser.push_prices(datetime.now(), check_targets = False)
    else:
        ozon_parser.push_prices(datetime.now(), check_targets = False)

    print(f'The product costs {tuple(tracker.prices[product].values())[-1]}')


def _start_parsers(tracker: Tracker, delay: float, wildberries: bool = False):
    ozon_parser = None if wildberries else OzonParser(tracker = tracker)
    wildberries_parser = WildberriesParser(tracker = tracker)

    while True:
        timestamp = datetime.now()

        if ozon_parser is not None:
            ozon_parser.push_prices(timestamp)

        wildberries_parser.push_prices(timestamp)

        tracker.save()

        sleep(delay)

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)

    # TelegramBot(tracker).poll()


@main.command()
@argument('path', type = str, default = 'assets')
@option('--delay', '-d', type = float, help = 'interval between consequitive price checks in seconds', default = 3600)
@option('--wildberries', '-w', is_flag = True, help = 'disable all parsers except wildberries')
def start(path: str, delay: float, wildberries: bool):
    tracker = Tracker(path)

    parsing_thread = Thread(target = _start_parsers, args = (tracker, delay, wildberries))
    parsing_thread.start()

    TelegramBot(tracker).poll()


if __name__ == '__main__':
    main()
