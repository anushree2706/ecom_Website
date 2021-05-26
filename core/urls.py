from django.urls import path
from .views import (
    # ItemDetailView,
    item_detail,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    add_single_item_to_cart,
    AddCouponView,
    RequestRefundView,
    PaymentcodView,
    accounts,
    accountsedit,
    handlerequest,
    back,
    add_to_wish_list,
    remove_from_wish_list,
    wish_lists,
    # homes
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    # path('', homes, name='homes'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', item_detail, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add_single_item_to_cart/<slug>/', add_single_item_to_cart, name='add_single_item_to_cart'),
    path('paymentcod/<payment_option>/', PaymentcodView.as_view(), name='paymentcod'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('accounts/', accounts, name='accounts'),
    path('accountsedit/', accountsedit, name='accountsedit'),
    path('handlerequest/', handlerequest, name="HandleRequest"),
    path('back/', back, name="back"),

    path('add-to-wish-list/<slug>/', add_to_wish_list, name="add_to_wish_list"),
    path('remove-from-wish-list/<slug>/', remove_from_wish_list, name="remove_from_wish_list"),
    path('wishlists/', wish_lists, name="wish_lists"),


]