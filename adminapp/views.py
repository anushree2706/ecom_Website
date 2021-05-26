from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import inflect


@login_required
@staff_member_required
def delivery_response(request):
    try:
        order = Order.objects.filter(ordered=True, received=False).order_by('-ordered_date')
        page = request.GET.get('page', 1)
        paginator = Paginator(order, 6)
        try:
            ordered = paginator.page(page)

        except PageNotAnInteger:
            ordered = paginator.page(1)

        except EmptyPage:
            ordered = paginator.page(paginator.num_pages)
        return render(request, 'delivery_response.html', {'ordered': ordered})
    except:
        print('account except part')
        pass
    return render(request, 'delivery_response.html')


@login_required
@staff_member_required
def delivery_response_confirm(request, pk):
    x = pk
    return render(request, 'delivery_response_confirm.html', {'xyz': x})


@login_required
@staff_member_required
def complete_delivery(request, pk):
    order = get_object_or_404(Order, id=pk)
    order.received = True
    order.save()
    return redirect('adminapp:delivery_response')


@login_required
@staff_member_required
def admin_search(request):
    if request.method == "POST":
        srch = request.POST['srh']
        if srch:
             match = Order.objects.filter(Q(id__exact=srch)|
                                         Q(user__username__icontains=srch)
                                         )
             no_of_item = match.count()
             print('no of item searched is ', no_of_item)
             if match:
                 messages.success(request, str(no_of_item) + " results found for " + srch)
                 return render(request, 'admin_search.html', {'sr': match})
             else:
                 messages.warning(request, 'No result found for '+ srch)
                 return redirect('adminapp:delivery_response')
        else:
            messages.warning(request, 'please type username or order id to check the status')
            return redirect('adminapp:delivery_response')

    return redirect('adminapp:delivery_response')


@login_required
@staff_member_required
def customer_detail(request, pk):
    customer_detail = get_object_or_404(Order, id=pk)
    return render(request, 'delivery_response.html', {'customer_detail':customer_detail})


@login_required
@staff_member_required
def generate_bill(request, pk):
    order = get_object_or_404(Order, pk=pk)
    now = timezone.now()
    tot = order.get_total()
    p = inflect.engine()
    amount_in_number=p.number_to_words(tot)
    print('timebfdgsfdgsfdgsfdgsfdgsfdgdgsfdgsfdg', now)
    return render(request, 'generate_bill.html', {'order':order, 'now':now, 'amount_in_number':amount_in_number})
