from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import ExtendedUser
import random
from django.contrib.auth.decorators import login_required
from core.models import Order, Address
import requests
from django.core.mail import send_mail


def homepage(request):
    return render(request, 'login.html')


def account_login(request):
    if request.method == "POST":
        user = auth.authenticate(username=request.POST['uname'], password=request.POST['pass'])
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You have logged in successfully')
            return redirect('/')
        else:
            messages.warning(request, "Invalid Login credentials.")
            return redirect('accounts:account_login')
    else:
        return render(request, 'account_login.html')


def account_signup(request):
    if request.method == "POST":
        if request.POST['pass'] == request.POST['passwordagain']:
            if User.objects.filter(username=request.POST['uname']).exists():
                messages.warning(request, 'Username has already taken')
                return render(request, 'account_signup.html')

            elif User.objects.filter(email=request.POST['email']).exists():
                messages.warning(request, 'Email has already taken, please type your exact email address')
                return render(request, 'account_signup.html')
            else:
                # user = User.objects.create_user(username=request.POST['uname'], password=request.POST['pass'])

                username = request.POST['uname']
                email = request.POST['email']
                password = request.POST['pass']
                phone = request.POST['phone']
                # newextendeduser = Extendeduser(phone_num=phone,age=age, user=user)
                print()
                generated_otp = random.randint(1111, 9999)
                print('generated otp is ', generated_otp)

                url = "https://www.fast2sms.com/dev/bulk"
                payload = "sender_id=FSTSMS&message=hi your OTP is {} &language=english&route=p&numbers={}".format(
                    generated_otp,
                    phone)
                headers = {
                    'authorization': "4x3CrQ8w8qX4ak577JiULwXK1ke1IhmE8oTjejcvGV74vg4yxacfL7GtM1jF",
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Cache-Control': "no-cache",
                }
                response = requests.request("POST", url, data=payload, headers=headers)

                return render(request, 'account_otp.html',
                              {'generated_otp': generated_otp, 'phone': phone, 'username': username, 'email': email,
                               'password': password})

        else:
            messages.warning(request, "Password didn't match")
            return render(request, 'account_signup.html')
    else:
        return render(request, 'account_signup.html')


def account_otp(request):
    if request.method == "POST":
        user_otp = request.POST["otp"]
        generated_otp = request.POST["generated_otp"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        phone = request.POST["phone"]

        if user_otp == generated_otp:
            user = User.objects.create_user(username=username, email=email, password=password)
            newextendeduser = ExtendedUser(phone_num=phone, user=user)
            newextendeduser.save()
            auth.login(request, user)
            messages.success(request, 'Your BIBZ account is created')
            return redirect('/')
        else:
            messages.info(request, "hey! you typed invalid otp try again ")
            return render(request, 'account_otp.html.',
                          {'generated_otp': generated_otp, 'phone': phone, 'username': username, 'email': email,
                           'password': password})
    return render(request, 'account_otp.html')


def account_signout(request):
    return render(request, 'account_signout.html')


def account_signout_confirm(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('/')


def contact(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['email']
        sub = request.POST['subject']

        sender = "vishnusumavausinfotech@gmail.com"
        receiver = ["info@vausinfotech.com", "dilipsapkota.d@gmail.com", "neelakanth@vausinfotech.com"]
        message = "\nfirst name:" + fname + "\nlast name: " + lname + "\nemail: " + email + "\nmessage: " + sub
        print('full message:', message)

        send_mail('Enquiry related BIBZ', message, sender, receiver)
        messages.success(request, 'Thanks You for being touched with us, our team will respond back you..')
    return render(request, 'contact.html')


def orders(request, pk):
    order = get_object_or_404(Order, id=pk)
    address = Address.objects.filter(user=request.user)[0]
    obj = User.objects.get(id=request.user.id)
    phone = ExtendedUser.objects.get(user=obj)
    return render(request, 'orders.html', {'order': order, 'address': address, 'address_phone': phone})


def success(request):
    messages.success(request, "Your password reset done successfully")
    return redirect('accounts:account_login')


def terms(request):
    return render(request, 'terms.html')
