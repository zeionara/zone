import os
from datetime import datetime

from pandas import DataFrame, read_csv


class Tracker:
    group = True

    def __init__(self, path: str):
        trackers = {}

        for file in os.listdir(path):
            if file.endswith('.txt'):
                user = int(file.split('.')[0])

                trackers[user] = UserTracker(path = os.path.join(path, file))

        self.path = path
        self.trackers = trackers

    def ignore(self, user: int, product: str):
        tracker = self.trackers.get(user)

        if tracker is None:
            raise ValueError(f'Unknown user: {user}')

        tracker.ignore(product)

    def track(self, user: int, product: str):
        tracker = self.trackers.get(user)

        if tracker is None:
            raise ValueError(f'Unknown user: {user}')

        tracker.track(product)

    def push(self, product: str, price: float, timestamp: datetime):
        for tracker in self.trackers.values():
            if product in tracker.products:
                tracker.push(product, price, timestamp)

    def spawn(self, user: int):
        if user in self.trackers:
            raise ValueError(f'Cannot overwrite tracker for user {user}')

        self.trackers[user] = UserTracker(path = os.path.join(self.path, f'{user}.txt'))

    def save(self):
        for tracker in self.trackers.values():
            tracker.save()

    @property
    def products(self):
        products = {product for tracker in self.trackers.values() for product in tracker.products}
        return tuple(products)

    def __contains__(self, user: int):
        return user in self.trackers

    def __getitem__(self, user: int):
        return self.trackers.get(user)


class UserTracker:
    group = False

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

    def ignore(self, product: str):
        if product not in self.products:
            raise ValueError(f'Not tracking product {product}')

        self.products.remove(product)

        self.save()

    def track(self, product: str):
        if product in self.products:
            raise ValueError(f'Already tracking product {product}')

        self.products.append(product)
        self.prices[product] = {}

        self.save()

    def push(self, product: str, price: float, timestamp: datetime):
        self.prices[product][timestamp.strftime('%d-%m-%Y %H:%M:%S')] = price

    def _load(self):

        # Read products

        if os.path.isfile(self.products_path):
            with open(self.products_path, 'r', encoding = 'utf-8') as file:
                self.products = [product[:-1] for product in file.readlines() if len(product) > 0]
        else:
            self.products = []

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
            file.write(f'{"" if products is None else products}\n')

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
