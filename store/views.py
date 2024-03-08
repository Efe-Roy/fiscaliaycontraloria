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
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    ItemSerializer, OrderSerializer, ItemDetailSerializer, AddressSerializer,
    PaymentSerializer, ShopSerializer, OrderItemSerializer, CouponSerializer
)
from store.models import Item, OrderItem, Order, Address, Payment, Coupon, Shop

import random
import string


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'PageSize'
    # max_page_size = 100

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
        shop = Shop.objects.get(user=user)
        queryset = Item.objects.all().order_by("-id")

        if user.is_vendor:
            queryset = queryset.filter(shop_id=shop.id)


        # Filter based on request parameters
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        return queryset


    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()

    #     # Count instances where state.name is "EJECUCION"
    #     ejecucion_count = queryset.filter(state__name="EJECUCION").count()

    #     # Count instances where state.name is "EJECUCION"
    #     terminado_count = queryset.filter(state__name="TERMINADO").count()

    #     # Count instances of each processType
    #     process_counts = queryset.values('process__name').annotate(process_count=Count('process'))

    #     # Count instances of each resSecType
    #     responsible_secretary_counts = queryset.values('responsible_secretary__name').annotate(responsible_secretary_count=Count('responsible_secretary'))

    #     # Count instances of each stateType
    #     state_counts = queryset.values('state__name').annotate(state_count=Count('state'))
       
    #     # Count instances of each typologyType
    #     typology_counts = queryset.values('typology__name').annotate(typology_count=Count('typology'))

    #     # Count instances where sex is "Masculino"
    #     male_count = queryset.filter(sex="Masculino").count()

    #     # Count instances where sex is "Femenino"
    #     female_count = queryset.filter(sex="Femenino").count()

    #     # Count all
    #     count = queryset.count()

    #     # Calculate the accumulated value of contract_value_plus
    #     accumulated_value = queryset.aggregate(
    #         total_accumulated_value=Sum(
    #             Cast('contract_value_plus', output_field=DecimalField(max_digits=15, decimal_places=2))
    #         )
    #     )['total_accumulated_value'] or Decimal('0.00')  # Default to 0.00 if no valid values are found

    #     # queryset = queryset.extra(
    #     #     select={'contact_no_integer': "substring(contact_no from '\\d+')::integer"},
    #     #     order_by=['contact_no_integer', 'contact_no']
    #     # )

    #     queryset = queryset.order_by('contact_no')

    #     serializer = self.get_serializer(queryset, many=True)
    #     response_data = {
    #         'results': serializer.data,
    #         'accumulated_value': str(accumulated_value),  # Convert Decimal to string for serialization
    #         'ejecucion_count': ejecucion_count,
    #         'terminado_count': terminado_count,
    #         'process_counts': process_counts,
    #         'responsible_secretary_counts': responsible_secretary_counts,
    #         'state_counts': state_counts,
    #         'typology_counts': typology_counts,
    #         'male_count': male_count,
    #         'female_count': female_count,
    #         'count': count
    #     }

    #     return Response(response_data)


class ItemCreatView(APIView):
    def post(self, request, *args, **kwargs):
        shop_id = request.data.get('shop')
        # user = request.user
        instance = Shop.objects.get(id=shop_id)
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['shop'] = instance  
            serializer.save()

            return Response(serializer.data, status= HTTP_201_CREATED)
        return Response(serializer.errors, status= HTTP_400_BAD_REQUEST)
    

class ItemDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ItemDetailSerializer
    queryset = Item.objects.all()


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

class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        # create the payment
        payment = Payment()
        payment.user = self.request.user
        payment.amount = order.get_total()
        payment.save()

        # assign the payment to the order

        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.billing_address = billing_address
        order.shipping_address = shipping_address
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

class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer

    def get_queryset(self):
        address_type = self.request.query_params.get('address_type', None)
        qs = Address.objects.all()
        if address_type is None:
            return qs
        return qs.filter(user=self.request.user, address_type=address_type)


class AddressCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Address.objects.all()


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)