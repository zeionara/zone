from click import group, argument, option
from time import sleep

from .OzonParser import OzonParser


@group()
def main():
    pass


@main.command()
@argument('product', type = str)
def parse(product: str):
    parser = OzonParser()
    parser.push_price(product)

    print(f'The product costs {parser.prices[-1]}')


@main.command()
@argument('product', type = str)
@option('--delay', '-d', type = float, help = 'interval between consequitive price checks in seconds', default = 3600)
def start(product: str, delay: float):
    parser = OzonParser()

    while True:
        parser.push_price(product)
        print(parser.prices)
        sleep(delay)


if __name__ == '__main__':
    main()
