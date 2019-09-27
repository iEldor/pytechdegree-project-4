import csv
import datetime
import os
from collections import OrderedDict
from decimal import Decimal

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()  # # primary_key=True is implied.
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateField()

    class Meta:
        database = db


def convert_to_cents(dollar_amount):
    dollar_amount = dollar_amount.replace('$','')
    try:
        dollar_amount = Decimal(dollar_amount)
        dollar_amount = int(dollar_amount * 100)
    except ValueError:
        dollar_amount = 0
    return dollar_amount


def extract_transform():
    with open('inventory.csv', newline='') as csvfile:
        inventory = csv.DictReader(csvfile)
        rows = list(inventory)
        for row in rows:
            row['product_quantity'] = int(row['product_quantity'])
            row['product_price'] = convert_to_cents(row['product_price'])
            row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y').date()
    return rows


def initialize():
    """Create the db objects if they do not exist"""
    db.connect()
    db.create_tables([Product], safe = True)
    inventory = extract_transform()
    for product in inventory:
        try:
            Product.create(
            product_name = product['product_name'],
            product_quantity = product['product_quantity'],
            product_price = product['product_price'],
            date_updated = product['date_updated']
        )
        except IntegrityError:
            product_record = Product.get(product_name = product['product_name'])
            if product_record.date_updated < product['date_updated']:
                product_record.product_quantity = product['product_quantity']
                product_record.product_price = product['product_price']
                product_record.date_updated = product['date_updated']
                product_record.save()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_loop():
    """Show the menu"""
    choice = None
    while choice != 'q':
        clear()
        print("Enter 'q' to quit")
        for key, value in menu.items():
            print(f'{key}) {value.__doc__}')
        choice = input('Action: ').lower().strip()
        
        if choice in menu:
            clear()
            menu[choice]()


def view_details():
    """View detail of a single product"""
    pass


def add_product():
    """Add a new product"""
    pass


def backup_db():
    """To make a backup of the entire database"""


menu = OrderedDict([
    ('v', view_details),
    ('a', add_product),
    ('b', backup_db)
])

if __name__ == '__main__':
    initialize()
    menu_loop()