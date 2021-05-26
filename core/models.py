from django.conf import settings
from django.db import models
from django.shortcuts import reverse


SIZE_CHOICES = (
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra large'),
    ('XXL', 'X-Extra large')
)


LABEL_CHOICES = (
    ('White', 'White'),
    ('Yellow', 'Yellow'),
    ('Blue', 'Blue'),
    ('Red', 'Red'),
    ('Green', 'Green'),
    ('Black', 'Black'),
    ('Brown', 'Brown'),
    ('Azure', 'Azure'),
    ('Ivory', 'Ivory'),
    ('Teal', 'Teal'),
    ('Silver', 'Silver'),
    ('Purple', 'Purple'),
    ('Navy blue', 'Navy blue'),
    ('Pea green', 'Pea green'),
    ('Gray', 'Gray'),
    ('Orange', 'Orange'),
    ('Maroon', 'Maroon'),
    ('Charcoal', 'Charcoal'),
    ('Aquamarine', 'Aquamarine'),
    ('Coral', 'Coral'),
    ('Fuchsia', 'Fuchsia'),
    ('Wheat', 'Wheat'),
    ('Lime', 'Lime'),
    ('Crimson', 'Crimson'),
    ('Khaki', 'Khaki'),
    ('Hot pink', 'Hot pink'),
    ('Magenta', 'Magenta'),
    ('Olden', 'Olden'),
    ('Plum', 'Plum'),
    ('Olive', 'Olive'),
    ('Cyan', 'Cyan'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=20)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    image1 = models.ImageField(blank=True, null=True)
    image2 = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={'slug': self.slug})


class Variation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.CharField(max_length=120, choices=SIZE_CHOICES)

    def __unicode__(self):
        return self.size


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.ForeignKey(Variation, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_taxable_amount(self):
        if self.item.discount_price:
            # return int(self.get_total_discount_item_price()-(self.get_total_discount_item_price()*(tax/100)))
            taxable = self.get_total_discount_item_price() / 1.18
            taxable_amount = round(taxable, 2)
            return taxable_amount
        else:
            taxable = self.get_total_item_price() / 1.18
            taxable_amount = round(taxable, 2)
            return taxable_amount

    def get_tax_amount(self):
        if self.item.discount_price:
            taxable = self.get_total_discount_item_price() * 18 / 118
            taxable_amount = round(taxable, 2)
            return taxable_amount
        else:
            taxable = self.get_total_item_price() * 18 / 118
            taxable_amount = round(taxable, 2)
            return taxable_amount


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment_mode = models.CharField(max_length=20, default='NOT PROCESSED')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    order_id = models.CharField(max_length=255)
    txn_id = models.CharField(max_length=255)
    txn_amount = models.CharField(max_length=255)
    pmt_mode = models.CharField(max_length=255)
    txn_date = models.DateTimeField(auto_now_add=True)
    txn_status = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
