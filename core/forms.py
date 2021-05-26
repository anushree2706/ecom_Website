from django import forms


PAYMENT_CHOICES = (
    ('COD', 'Cash On Delivery'),
    ('P', 'Online')
)


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_phone = forms.CharField(required=False)
    shipping_state = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
