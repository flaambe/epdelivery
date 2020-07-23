from rest_framework import serializers

from .models import City, User, Status, Category, Subcategory, Product, Order

# Serializers define the API representation.
class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'emoji']

class SubcategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'category', 'name', 'emoji']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'subcategory', 'name', 'description', 'image', 'price', 'active']

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'phone_number', 'address', 'comment', 'created_at']

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'city', 'first_name', 'username', 'telegram_id', 'chat_id']

class StatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']