import csv
import datetime
import os
import sys
from collections import OrderedDict
from decimal import Decimal

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()  # primary_key=True is implied.
    product_name = CharField(unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateField()

    class Meta:
        database = db


def convert_price_to_cents(dollar_amount):
    dollar_amount = dollar_amount.replace('$','')
    try:
        dollar_amount = Decimal(dollar_amount)
        dollar_amount = int(dollar_amount * 100)
    except ValueError:  #  handles unexpected invalid product_price from csv file
        dollar_amount = 0  #  alternatively bad records can be placed to exception table
    return dollar_amount


def convert_quantity_to_int(quantity):
    try:
        quantity = int(quantity)
    except ValueError:  #  handles unexpected invalid product_quantity from csv file
        quantity = 0  #  alternatively bad records can be placed to exception table
    return quantity


def convert_date_updated(date_updated):
    try:
        date_updated = datetime.datetime.strptime(date_updated, '%m/%d/%Y').date()
    except ValueError:  #  handles unexpected invalid date_updated from csv file
        date_updated = datetime.datetime.now().date()    #  alternatively bad records can be placed to exception table
    return date_updated


def extract_transform():
    with open('inventory.csv', newline='') as csvfile:
        inventory = csv.DictReader(csvfile)
        rows = list(inventory)
        for row in rows:
            row['product_quantity'] = convert_quantity_to_int(row['product_quantity'])
            row['product_price'] = convert_price_to_cents(row['product_price'])
            row['date_updated'] = convert_date_updated(row['date_updated'])
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
            if product_record.date_updated <= product['date_updated']:  #  most recent data is loaded
                product_record.product_quantity = product['product_quantity']
                product_record.product_price = product['product_price']
                product_record.date_updated = product['date_updated']
                product_record.save()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_loop():
    """Show the menu"""
    clear()
    choice = None
    while choice != 'q':
        print('\n########## Store Inventory ##########'.upper())
        print("\nEnter 'q' to quit")
        for key, value in menu.items():
            print(f'{key}) {value.__doc__}')
        choice = input('\nAction: ').lower().strip()
        
        if choice in menu:
            clear()
            menu[choice]()
        elif choice != 'q':
            clear()
            print(f'Sorry [{choice}] is not a valid choice! Please try again.')
            continue
    clear()
    print('\n########## Exit Successful ##########'.upper())


def view_details():
    """View detail of a single product"""
    while True:
        user_input = input('Please enter product id > ')
        try:
            product_id = int(user_input)
            product_record = Product.get_by_id(product_id)
            print(f'''
            ================ PRODUCT ID: {product_record.product_id} ================
            name:           {product_record.product_name}
            quantity:       {product_record.product_quantity}
            price:          {product_record.product_price}
            update date:    {product_record.date_updated}  
            ''')
            input('Hit ENTER to return to main menu > ')
            clear()
            break
        except ValueError:
            clear()
            print(f'Sorry, [{user_input}] is not a valid entry! Please try again.')
            continue
        except DoesNotExist:
            clear()
            print(f'Sorry, product with product id [{user_input}] does not exist! Please try again.')
            continue


def add_product():
    """Add a new product"""
    while True:
        product_name = input('Please input product name > ').strip()
        if not product_name:
            clear()
            print('Sorry, Product Name should not be empty!')
            continue
        break
    while True:
        try:
            product_quantity = input('Please input product quantity > ')
            product_quantity = int(product_quantity)
            if product_quantity < 0: raise ValueError  #  we do not want negative quantities
            break
        except ValueError:
            clear()
            print(f'Sorry, [{product_quantity}] is not a valid product quantity! Please try again.')
            continue
    while True:
        try:
            user_input = input('Please input product price in dollars e.g. $3.25 > ')
            product_price = user_input.replace('$','')
            product_price = Decimal(product_price)
            product_price = int(product_price * 100)
            if product_price < 0: raise ValueError  #  we do not want negative price
            break
        except Exception:
            clear()
            print(f'Sorry, [{user_input}] is not a valid product price! Please try again.')
            continue
    date_updated = datetime.datetime.now().date()
    try:
        Product.create(
        product_name = product_name,
        product_quantity = product_quantity,
        product_price = product_price,
        date_updated = date_updated
    )
        clear()
        input('Record was successfully added. Hit Enter to continue ... > ')
    except IntegrityError:
        product_record = Product.get(product_name = product_name)
        if product_record.date_updated <= date_updated:  #  most recent data is loaded
            product_record.product_quantity = product_quantity
            product_record.product_price = product_price
            product_record.date_updated = date_updated
            product_record.save()
            clear()
            input('Record was successfully updated. Hit Enter to continue ... > ')


def backup_db():
    """To make a backup"""
    with open('backup.csv', 'w') as csvfile:  #  load type: truncate and insert
        fieldnames = ['product_id', 'product_name', 'product_quantity', 'product_price', 'date_updated']
        backupwriter = csv.DictWriter(csvfile, lineterminator='\n', fieldnames = fieldnames)
        backupwriter.writeheader()
        entries = Product.select()
        for entry in entries:
            backupwriter.writerow({
                'product_id': entry.product_id,
                'product_name': entry.product_name,
                'product_quantity': entry.product_quantity,
                'product_price': entry.product_price,
                'date_updated': entry.date_updated
            })
        clear()
    input("Backup is successfull. Hit Enter to continue > ")


menu = OrderedDict([
    ('v', view_details),
    ('a', add_product),
    ('b', backup_db)
])


if __name__ == '__main__':
    try:
        initialize()
        menu_loop()
    except Exception:
        clear()
        print('########## Exit Successful ##########'.upper())
        sys.exit()