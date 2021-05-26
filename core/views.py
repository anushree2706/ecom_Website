from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from accounts.models import ExtendedUser
from .forms import CheckoutForm
from .models import Item, OrderItem, Order, Address, Payment, Variation, WishList
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
from django.contrib.auth.models import User
import datetime

mid = 'fGrIzA97726764689450'
merchent_key = 'NjeNJa4DJmq53!yu'


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("/")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        # address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_phone = form.cleaned_data.get(
                        'shipping_phone')
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_phone, shipping_state, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            phone=shipping_phone,
                            state=shipping_state,
                            zip=shipping_zip,
                            # address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        print('Deepak :', set_default_shipping)
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")
                        return redirect('core:checkout')

                payment_option = form.cleaned_data.get('payment_option')
                print('payment option :', payment_option)
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'COD':
                    return redirect('core:paymentcod', payment_option='COD')
                elif payment_option == 'P':
                    current_time = str(datetime.datetime.now())
                    updated_id = ''.join(
                        [current_time[:10], current_time[11:13], current_time[14:16], current_time[17:], str(order.id)])

                    param_dict = {
                        'MID': mid,
                        'ORDER_ID': str(updated_id),
                        'TXN_AMOUNT': str(order.get_total()),
                        'CUST_ID': self.request.user.email,
                        'INDUSTRY_TYPE_ID': 'Retail',
                        'WEBSITE': 'WEBSTAGING',
                        'CHANNEL_ID': 'WEB',
                        'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

                    }
                    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, merchent_key)
                    return render(self.request, 'paytm.html', {'param_dict': param_dict})

                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
    print(response_dict, "inside handle request")
    return render(request, 'paymentstatus.html', {'response': response_dict})


@csrf_exempt
def back(request):
    if request.method == 'POST':
        form = request.POST
        response_dict = {}
        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                checksum = form[i]
        print("inside back view printed ", response_dict)
        verify = Checksum.verify_checksum(response_dict, merchent_key, checksum)

        if verify:
            print("just before if")
            if response_dict['RESPCODE'] == '01':
                print("inside verify method")
                # create the payment
                payment = Payment()
                order_id_post = form['ORDERID']
                in_order_id_post = int(order_id_post[23:])
                payment.order_id = in_order_id_post
                payment.txn_id = form['TXNID']
                payment.txn_amount = form['TXNAMOUNT']
                payment.pmt_mode = form['PAYMENTMODE']
                payment.txn_date = form['TXNDATE']
                payment.txn_status = form['STATUS']
                payment.user = request.user
                obj = Payment.objects.filter(user=request.user, order_id=int(order_id_post[23:]))
                if not obj.exists():
                    payment.save()

                    # assign the payment to the order
                    order = Order.objects.get(id=in_order_id_post)
                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()

                    order.ordered = True
                    order.ordered_date = timezone.now()
                    order.payment_mode = 'ONLINE'
                    order.payment = payment
                    order.save()
                    print('order successful')
                    messages.info(request, 'Your order is successful')
            else:
                print('order was not successful because' + response_dict['RESPMSG'])
                messages.warning(request, 'Your Order is Filure')
        return render(request, 'back.html', {'response': response_dict})
    return redirect('core:accounts')


class PaymentcodView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except:
            messages.warning(self.request, "You have an empty cart")
            return redirect("/")

        if order.shipping_address:
            context = {
                'order': order
            }
            return render(self.request, "payment_cod.html", context)
        else:
            messages.warning(
                self.request, "You have not added a shipping address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order.save()

        # payment method
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
        order.ordered_date = timezone.now()
        order.payment_mode = 'COD'
        order.save()
        # payment method ends
        messages.success(self.request, "Your order was successful!")
        return redirect("/")


class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = "home.html"
    ordering = ['-id']


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def item_detail(request, slug):
    item = get_object_or_404(Item, slug=slug)
    color_slug = slug.split("-")[0]
    color_obj = Item.objects.filter(slug__startswith=color_slug)
    return render(request, 'product.html', {'item': item, 'object': item, 'color_object': color_obj})


@login_required(login_url="/accounts/account_login")
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == "POST":
        size = request.POST['size']
        size_obj = Variation.objects.filter(size=size, item=item)[0]
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            size=size_obj,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug, size__size=size).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:order-summary")
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect("core:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")


@login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == "POST":
        add_size = request.POST['add']
        size_obj = Variation.objects.filter(size=add_size, item=item)[0]
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug, size__size=add_size).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                size=size_obj,
                ordered=False
            )[0]
            if order_item.quantity >= 1:
                order_item.quantity += 1
                order_item.save()
            else:
                order.items.add(order_item)

            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == "POST":
        remove_size = request.POST['size']
        size_obj = Variation.objects.get(size=remove_size, item=item)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug, size__size=remove_size).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    size=size_obj,
                    ordered=False
                )[0]
                order.items.remove(order_item)
                if order_item.quantity >= 1:
                    order_item.delete()

                print('order items are :', OrderItem.objects.filter(user=request.user))
                messages.info(request, "This item was removed from your cart.")
                return redirect("core:order-summary")
            else:
                messages.info(request, "This item was not in your cart")
                return redirect("core:product", slug=slug)
        else:
            messages.info(request, "You do not have an active order")
            return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == "POST":
        remove_size = request.POST['remove']
        size_obj = Variation.objects.filter(size=remove_size, item=item)[0]
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug, size__size=remove_size).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                size=size_obj,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                # order.items.remove(order_item)
                order.items.filter(item__slug=item.slug, size__size=remove_size).delete()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


def accounts(request):
    try:
        ordered = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
        s_address = Address.objects.filter(user=request.user, default=1)
        print('account obj part')
        if s_address.exists():
            print('account if part')
            address = s_address[0]
            obj = User.objects.get(id=request.user.id)
            phone = ExtendedUser.objects.get(user=obj)

            return render(request, 'accounts.html', {'ordered': ordered, 'phone': phone, 'address': address})
        else:
            print('account else part')
            obj = User.objects.get(id=request.user.id)
            phone = ExtendedUser.objects.get(user=obj)
            return render(request, 'accounts.html', {'ordered': ordered, 'phone': phone})
    except:
        print('account axcept part')
        pass
    return render(request, 'accounts.html')


def accountsedit(request):
    if request.method == "POST":
        shipping_address = request.POST['shipping_address']
        shipping_address2 = request.POST['shipping_address2']
        shipping_state = request.POST['shipping_state']
        shipping_phone = request.POST['shipping_phone']
        shipping_zip = request.POST['shipping_zip']
        print("my updated street address is ", shipping_address)
        print(request.user)

        obj_s = Address.objects.filter(user=request.user.id).update(street_address=shipping_address,
                                                                    apartment_address=shipping_address2,
                                                                    state=shipping_state,
                                                                    phone=shipping_phone, zip=shipping_zip)
        return redirect('core:accounts')

    return render(request, 'accounts_edit.html')


def search(request):
    if request.method == "POST":
        srch = request.POST['srh']
        if srch:
            match = Item.objects.filter(Q(title__icontains=srch) |
                                        Q(label__icontains=srch)
                                        )
            no_of_item = match.count()
            print('no of item searched is ', no_of_item)
            if match:
                messages.success(request, str(no_of_item) + " results found for " + srch)
                wish_list_object = WishList.objects.all()
                return render(request, 'home.html', {'sr': match, 'wish_list_object': wish_list_object})
            else:
                messages.warning(request, 'No result found')
                return redirect('/')
        else:
            return redirect('/')
    return redirect('/')


@login_required(login_url="/accounts/account_login")
def add_to_wish_list(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if not WishList.objects.filter(user=request.user, item=item):
        wish_list = WishList(user=request.user, item=item)
        wish_list.save()
    return redirect('/')


@login_required(login_url="/accounts/account_login")
def remove_from_wish_list(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wishlish_item = get_object_or_404(WishList, item=item)
    if wishlish_item:
        wishlish_item.delete()
    return redirect('core:wish_lists')


@login_required(login_url="/accounts/account_login")
def wish_lists(request):
    wishlist_item = WishList.objects.filter(user=request.user)
    return render(request, 'wish_list.html', {'wishlist_item': wishlist_item})
