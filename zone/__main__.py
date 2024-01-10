from time import sleep
from click import group, argument, option
from datetime import datetime

from .OzonParser import OzonParser
from .Tracker import Tracker


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


@main.command()
@argument('path', type = str, default = 'assets/products.txt')
@option('--delay', '-d', type = float, help = 'interval between consequitive price checks in seconds', default = 3600)
def start(path: str, delay: float):
    tracker = Tracker(path)
    parser = OzonParser(tracker = tracker)

    while True:
        timestamp = datetime.now()
        parser.push_prices(timestamp)

        tracker.save()

        sleep(delay)


if __name__ == '__main__':
    main()
