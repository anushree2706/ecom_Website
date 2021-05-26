from django.urls import path
from .views import delivery_response, delivery_response_confirm, complete_delivery, generate_bill, admin_search, customer_detail

app_name = 'adminapp'
urlpatterns=[
    path('delivery-response/', delivery_response, name='delivery_response'),
    path('delivery-response-confirm/<int:pk>/', delivery_response_confirm, name='delivery_response_confirm'),
    path('complete-delivery/<int:pk>/', complete_delivery, name='complete_delivery'),
    path('generate-bill/<int:pk>/', generate_bill, name='generate_bill'),

    path('admin-search/', admin_search, name='admin_search'),
    path('customer-detail/<int:pk>/', customer_detail, name='customer_detail'),
]