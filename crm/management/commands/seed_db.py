import os
import django
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from faker import Faker

from crm.models import Customer, Product, Order

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

fake = Faker()

class Command(BaseCommand):
    help = 'seed and populate customers, products, and orders'

    def handle(self, *args, **options):
        self.stdout.write('Seeding customer data...')
        self.create_customer()
        self.stdout.write('Seeding product data...')
        self.create_product()
        self.stdout.write('Seeding order data...')
        self.create_order()
        self.stdout.write(self.style.SUCCESS('Done seeding database!'))
    
    def create_customer(self):
        created_count = 0
        attempted_count = 0
        max_attempts = 20

        while created_count < 10 and attempted_count < max_attempts:
            attempted_count += 1
            try:
                customer = Customer.objects.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    phone=fake.phone_number(),
                )
                created_count += 1
                
                if created_count % 5 == 0:
                    self.stdout.write(f'created {created_count} customers....')

            except IntegrityError as e:
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'error creating customer: {e}'))
    
    def create_product(self):
        created_count = 0
        attempted_count = 0
        max_attempts = 20   

        while created_count < 10 and attempted_count < max_attempts:
            attempted_count += 1
            try:
                product = Product.objects.create(
                    name=fake.word().capitalize() + ' ' + fake.word().capitalize(),
                    price=fake.random_number(digits=3) + 0.99,
                    stock=fake.random_int(min=0, max=100)
                )
                created_count += 1
                
                if created_count % 5 == 0:
                    self.stdout.write(f'created {created_count} products....')

            except IntegrityError as e:
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'error creating product: {e}'))

    def create_order(self):
        created_count = 0
        attempted_count = 0
        max_attempts = 20   

        while created_count < 10 and attempted_count < max_attempts:
            attempted_count += 1
            try:
                customer = Customer.objects.order_by('?').first()
                products = list(Product.objects.order_by('?')[:3])  # Randomly select 3 products
                
                if not customer or not products:
                    continue
                
                # Calculate total amount first
                total_amount = sum(product.price for product in products)
                
                # Create and save the order first
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total_amount
                )
                
                # Now add the products (order has an ID at this point)
                order.products.add(*products)
                
                created_count += 1
                
                if created_count % 5 == 0:
                    self.stdout.write(f'created {created_count} orders....')

            except IntegrityError as e:
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'error creating order: {e}'))