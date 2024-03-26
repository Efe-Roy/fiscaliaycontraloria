from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView, ListCreateAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    ItemSerializer, OrderSerializer, ItemDetailSerializer, AddressSerializer,
    PaymentSerializer, ShopSerializer, OrderItemSerializer, CouponSerializer
)
from store.models import Item, OrderItem, Order, Address, Payment, Coupon, Shop
from Auth.serializers import UserSerializer
from decimal import Decimal

import random
import string


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'PageSize'
    # max_page_size = 100

class ShopCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid():
            user_data = {
                'username': request.data.get('username'), 
                'email': request.data.get('email'), 
                'password': request.data.get('password'), 
                'is_vendor': True
            }
            user_serializer = UserSerializer(data=user_data)
            if user_serializer.is_valid():
                user = user_serializer.save() 
                user.set_password(user_data['password']) 
                user.save() 
                serializer.save(user=user) 
                return Response(serializer.data, status=HTTP_201_CREATED)
            else:
                return Response(user_serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
class ShopListView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ShopSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Shop.objects.all()

        # Filter based on request parameters
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    
class ShopDetailView(APIView):
    def get(self, request, format=None):
        user=request.user
        queryset = Shop.objects.get(user=user)
        serializer = ShopSerializer(queryset)
        return Response( serializer.data)

class ItemListView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user=self.request.user
        queryset = Item.objects.all().order_by("-id")

        if user.is_vendor:
            shop = Shop.objects.get(user=user)
            queryset = queryset.filter(shop_id=shop.id)


        # Filter based on request parameters
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        return queryset

class ItemCreatView(APIView):
    def post(self, request, *args, **kwargs):
        # shop_id = request.data.get('shop')
        user = request.user
        instance = Shop.objects.get(user=user)
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['shop'] = instance  
            serializer.save()

            return Response(serializer.data, status= HTTP_201_CREATED)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)
    
class ItemDetailView(APIView):
    def get_object(self, pk):
        try:
            return Item.objects.get(id=pk)
        except Item.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = ItemDetailSerializer(instance)
        return Response( serializer.data)

    def put(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = ItemDetailSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        instance = self.get_object(pk)
        instance.delete()
        return Response(status= HTTP_204_NO_CONTENT)

class OrderQuantityUpdateView(APIView):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(Item, id=pk)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item_id=item.id).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)

class OrderItemListView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = OrderItemSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = OrderItem.objects.all().order_by("-id")

        # Filter based on request parameters
        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id:
            queryset = queryset.filter(item__shop_id=shop_id, ordered=False)
        
        return queryset

class OrderItemDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = OrderItem.objects.all()


class AddToCartView(APIView):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(Item, id=pk)
        shop_instance = Shop.objects.get(id=item.shop.id)

        order_item_qs = OrderItem.objects.filter(
            item=item,
            user=request.user,
            ordered=False
        )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                ordered=False
            )
            order_item.save()

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date, shop=shop_instance)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)

class OrderListView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = OrderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Order.objects.all()

        # Filter based on request parameters
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id, ordered=False)
        
        user_id_2 = self.request.query_params.get('user_id_2', None)
        if user_id_2:
            queryset = queryset.filter(user_id=user_id_2)
            
        rider_id = self.request.query_params.get('rider_id', None)
        if rider_id:
            queryset = queryset.filter(rider_id=rider_id)
            
        ordered = self.request.query_params.get('ordered', None)
        if ordered:
            queryset = queryset.filter(ordered=True, received=False, being_delivered=False)
        
        being_delivered = self.request.query_params.get('being_delivered', None)
        if being_delivered:
            queryset = queryset.filter(being_delivered=True)
        
        received = self.request.query_params.get('received', None)
        if received:
            queryset = queryset.filter(received=True)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        being_delivered = queryset.filter(being_delivered=True).count()
        received = queryset.filter(received=True).count()
        all_count = queryset.count()

        # Order the queryset by id
        queryset = queryset.order_by('-id')

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'results': serializer.data,
                'being_delivered': being_delivered,
                'received': received,
                'all_count': all_count,
            }
            return self.get_paginated_response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'results': serializer.data,
            'being_delivered': being_delivered,
            'received': received,
            'all_count': all_count,
        }

        return Response(response_data)

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
            # return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)

class OrderUpdateView(APIView):
    def get(self, request, pk, format=None):
        instance = Order.objects.get(id=pk)
        instance.rider = self.request.user
        instance.being_delivered = True
        instance.save()
        return Response({"message": "Order successfully assigned to you!"} ,status=HTTP_200_OK)
    
class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        order = Order.objects.get(user=user, ordered=False)
        # print("acc_balance", user.acc_balance)
        # print("order total", order.get_total())
        
        if order.get_total() > user.acc_balance:
            return Response({'error': 'Insufficient balance'}, status=HTTP_400_BAD_REQUEST)
        
        user.acc_balance -= Decimal(order.get_total())
        user.save()
        # print("final acc_balance", user.acc_balance)

        
        # create the payment
        payment = Payment()
        payment.user = user
        payment.amount = order.get_total()
        payment.save()

        # assign the payment to the order
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
            # pass

        order.ordered = True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.save()

        return Response({"message": "Your order was successful!"} ,status=HTTP_200_OK)
        
class CreateCouponView(APIView):
    def get(self, request, format=None):
        queryset = Coupon.objects.all()
        serializerPqrs = CouponSerializer(queryset, many=True)
        return Response( serializerPqrs.data)

    def post(self, request, *args, **kwargs):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= HTTP_201_CREATED)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)
    
class CouponDetailView(APIView):
    def put(self, request, pk, format=None):
        inatance = Coupon.objects.get(id=pk)
        serializer = CouponSerializer(inatance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        inatance = Coupon.objects.get(id=pk)
        inatance.delete()
        return Response(status= HTTP_200_OK)
                        
class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(
            user=self.request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)

class AddressListView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user=self.request.user
        queryset = Address.objects.filter(user=user).order_by("-id")

        # Filter based on request parameters
        address_type = self.request.query_params.get('address_type', None)
        if address_type:
            queryset = queryset.filter(address_type=address_type)

        default = self.request.query_params.get('default', None)
        if default:
            queryset = queryset.filter(default=True)

        return queryset

class AddressCreateView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = user  
            serializer.save()

            return Response(serializer.data, status= HTTP_201_CREATED)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)
  
class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Address.objects.all()

class AddressDefaultAPIView(APIView):
    def get(self, request, pk, format=None):
        user=request.user
        qs = Address.objects.filter(user=user)

        for data in qs:
            data.default = False
            data.save()

        instance = Address.objects.get(id=pk)
        instance.default = True
        instance.save()

        return Response("Successfully updated for instances", status=HTTP_200_OK)
    
class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)