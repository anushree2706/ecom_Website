from django.urls import path
from .views import(
    account_signup,
    account_login,
    account_otp,
    account_signout,
    account_signout_confirm,
    contact,
    orders,
    success,
    terms,
    )

app_name = 'accounts'

urlpatterns = [
    path('account_signup/', account_signup, name='account_signup'),
    path('account_login/', account_login, name='account_login'),
    path('account_otp/', account_otp, name='account_otp'),
    path('account_signout/', account_signout, name='account_signout'),
    path('account_signout_confirm/', account_signout_confirm, name='account_signout_confirm'),
    path('contact/', contact, name='contact'),
    path('orders/<int:pk>/', orders, name='orders'),
    path('success/', success, name='success'),
    path('terms/', terms, name='terms'),
]