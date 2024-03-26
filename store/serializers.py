# from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from Auth.serializers import UserSerializer
from .models import (
    Address, Item, Order, OrderItem, Coupon, Payment, Shop, Category
)
from Auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'amount', 'shop']

class ItemSerializer(serializers.ModelSerializer):
    shop = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'inventory', 'discount_price', 'image', 'shop']

    def get_shop(self, obj):
        return ShopSerializer(obj.shop).data

class ShopSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ['id', 'user', 'name', 'image', 'description', 'stars', 'reviews', 'address']

    def get_user(self, obj):
        return UserSerializer(obj.user).data
    
    def get_address(self, obj):
        user_addresses = Address.objects.filter(user=obj.user)
        serializer = AddressSerializer(instance=user_addresses, many=True)
        return serializer.data

        
class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'item',
            'quantity',
            'final_price'
        )

    def get_item(self, obj):
        return ItemSerializer(obj.item).data

    def get_final_price(self, obj):
        return obj.get_final_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'order_items',
            'total',
            'ordered',
            'coupon',
            'being_delivered',
            'received',
            'ref_code',
            'ordered_date'
        )

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None
    
    def get_user(self, obj):
        return UserSerializer(obj.user).data


class ItemDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'name',
            'price',
            'discount_price',
            'category',
            'description',
            'image',
        )

    # def get_category(self, obj):
    #     return obj.get_category_display()
    
    def get_category(self, obj):
        return CategorySerializer(obj.category).data


    def get_label(self, obj):
        return obj.get_label_display()


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = (
            'id',
            'user',
            'address',
            'lng',
            'lat',
            'zip',
            'address_type',
            'default'
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'amount',
            'timestamp'
        )