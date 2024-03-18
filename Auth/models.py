from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def upload_to(instance, filename):
    return 'profile/{filename}'.format(filename=filename)

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    phone_num = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to=upload_to, null=True, blank=True)
