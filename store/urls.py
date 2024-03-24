from django.urls import path
from .views import (
    ItemListView, ItemDetailView, ItemCreatView,
    AddToCartView, ShopListView, ShopDetailView, ShopCreateView,
    OrderDetailView, OrderQuantityUpdateView, AddCouponView, 
    CreateCouponView, CouponDetailView, OrderListView, AddressDefaultAPIView,

    AddressListView, AddressCreateView, AddressUpdateView, AddressDeleteView,
    OrderItemDeleteView, OrderItemListView, PaymentListView, PaymentView
)

urlpatterns = [
    path('addresses/', AddressListView.as_view(), name='address-list'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/update/', AddressUpdateView.as_view(), name='address-update'),
    path('addresses/<pk>/defualt/', AddressDefaultAPIView.as_view()),
    path('addresses/<pk>/delete/',AddressDeleteView.as_view(), name='address-delete'),

    path('shops/', ShopListView.as_view()),
    path('shops-create/', ShopCreateView.as_view()),
    path('shop-detail/', ShopDetailView.as_view()),
    path('products/', ItemListView.as_view()),
    path('products-create/', ItemCreatView.as_view()),
    path('products/<pk>/', ItemDetailView.as_view()),

    path('add-to-cart/<pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('checkout/', PaymentView.as_view(), name='checkout'),

    path('create-coupon/', CreateCouponView.as_view()),
    path('detail-coupon/<pk>/', CouponDetailView.as_view()),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    
    path('order-items-list/', OrderItemListView.as_view()),
    path('order-items/<pk>/delete/', OrderItemDeleteView.as_view(), name='order-item-delete'),
    path('order-item/update-quantity/<pk>/', OrderQuantityUpdateView.as_view()),
    
    path('order-list/', OrderListView.as_view()),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
]