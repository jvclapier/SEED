from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date
from django.conf import settings

class Intern(AbstractUser):
    # username
    # password
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    email = models.EmailField()
    semester = models.TextField(blank=True, null=True)

class AssignedClient(models.Model):
    intern = models.ForeignKey('Intern', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)

class Client(models.Model):
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(blank=True, null=True, max_length=11)
    tagalog_needed = models.BooleanField(default=True)
    street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    barangay = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)
    lon = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)
    business_name = models.TextField(blank=True, null=True)
    business_type = models.TextField(blank=True, null=True)
    transportation_method = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # TODO: add image field

class Log(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_visited = models.DateField(blank=True, null=True)
    visit_description = models.TextField(blank=True, null=True)
    next_steps = models.TextField(blank=True, null=True)
    time_of_visit = models.TextField(blank=True, null=True)
    intern = models.ForeignKey('Intern', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
