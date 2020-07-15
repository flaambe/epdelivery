from django.db import models
from django.db.models import F, Sum, FloatField
from decimal import Decimal


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Store(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class User(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True)
    first_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, default='')
    telegram_id = models.PositiveIntegerField(unique=True)
    chat_id = models.PositiveIntegerField()
    last_phone_number = models.CharField(max_length=15)
    last_address = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.id}-{self.first_name}'


class Courier(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    comment = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    emoji = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    emoji = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sum(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(OrderProduct)
    courier = models.ForeignKey(
        Courier, on_delete=models.PROTECT, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s' % self.id


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sum(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True)

    @property
    def total_price(self):
        return self.products.aggregate(
            total_price=Sum(F('quantity') * F('price'),
                            output_field=FloatField())
        )['total_price'] or Decimal('0')

    def __str__(self):
        return f'{self.id}-{self.user}'
