from django.contrib import admin

from .models import City, Store, User, Courier, Category, Subcategory, Product, Status, Order, OrderProduct, Cart, CartProduct

# Register your models here.
admin.site.register(City)
admin.site.register(Cart)
admin.site.register(CartProduct)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'city', 'address')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'telegram_id', 'city')


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'city', 'comment')


admin.site.register(Category)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subcategory', 'image', 'price')


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ('status', 'phone_number', 'created_at', 'address', 'user', 'comment')


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):

    list_display = ('product', 'price', 'quantity')
