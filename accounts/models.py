from django.db import models
from django.contrib.auth.models import User


class ExtendedUser(models.Model):
    phone_num=models.CharField(max_length=15)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
