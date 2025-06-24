import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.validators import validate_email
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

def validate_phone(phone):
    if phone and not re.match(r'^\+?[0-9\- ]+$', phone):
        raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890")

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            validate_email(input.email)
            validate_phone(input.phone)
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except Exception as e:
            raise Exception(str(e))

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        customers = []
        errors = []
        
        for idx, customer_input in enumerate(input):
            try:
                validate_email(customer_input.email)
                validate_phone(customer_input.phone)
                
                customer = Customer(
                    name=customer_input.name,
                    email=customer_input.email,
                    phone=customer_input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        try:
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock if input.stock is not None else 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except Exception as e:
            raise Exception(str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
            products = Product.objects.filter(pk__in=input.product_ids)
            
            if not products.exists():
                raise Exception("At least one valid product must be selected")
            
            order = Order(customer=customer)
            order.save()
            order.products.set(products)
            
            # Recalculate total_amount after products are set
            order.total_amount = sum(product.price for product in products)
            order.save()
            
            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist")
        except Product.DoesNotExist:
            raise Exception("One or more products do not exist")
        except Exception as e:
            raise Exception(str(e))

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    all_customers = DjangoFilterConnectionField(CustomerType)

    products = graphene.List(ProductType)
    all_products = DjangoFilterConnectionField(ProductType)

    orders = graphene.List(OrderType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()