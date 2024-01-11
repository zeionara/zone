import os
from datetime import datetime

from pandas import DataFrame, read_csv


class Tracker:
    def __init__(self, path: str = None, products: list[str] = None):
        if products is None:
            self.products_path = path
            self.prices_path = f"{path[::-1].split('.', maxsplit = 1)[1][::-1]}.tsv"

            self._load()
        elif path is None:
            self.products_path = None
            self.prices_path = None

            self.products = products
            self.prices = {product: {} for product in self.products}

    def track(self, product: str):
        if product in self.products:
            raise ValueError(f'Already tracking product {product}')

        self.products.append(product)
        self.prices[product] = {}

    def push(self, product: str, price: float, timestamp: datetime):
        self.prices[product][timestamp.strftime('%d-%m-%Y %H:%M:%S')] = price

    def _load(self):

        # Read products

        with open(self.products_path, 'r', encoding = 'utf-8') as file:
            self.products = [product[:-1] for product in file.readlines() if len(product) > 0]

        # Read prices

        if os.path.isfile(self.prices_path):
            df = read_csv(self.prices_path, sep = '\t', index_col = 'date')
            prices = df.to_dict()

            for product in self.products:
                if product not in prices:
                    prices[product] = {}
        else:
            self.prices = {product: {} for product in self.products}

        self.prices = prices

    def save(self):
        # Save products

        products = None

        for product in self.products:
            if products is None:
                products = product
            else:
                products = f'{products}\n{product}'

        with open(self.products_path, 'w', encoding = 'utf-8') as file:
            file.write(f'{products}\n')

        # Save prices

        flat_dict = {}
        for column, row_dict in self.prices.items():
            for row, value in row_dict.items():
                flat_dict[(column, row)] = value

        df = DataFrame(list(flat_dict.items()), columns=['Column', 'Value'])

        df[['Col', 'Row']] = DataFrame(df['Column'].tolist(), index=df.index)
        df = df.drop('Column', axis=1)

        df_pivot = df.pivot(index='Row', columns='Col', values='Value')
        df_pivot.rename_axis('date', inplace = True)
        df_pivot.to_csv(self.prices_path, sep='\t')
