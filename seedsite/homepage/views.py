from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.mail import send_mail
import re
from django.template.loader import render_to_string, get_template
from django.conf import settings as django_settings
from homepage import models as mod

# Create your views here.

def index(request):

    clients = mod.Client.objects.all()

    context = {
        'clients':clients,
    }

    return render(request, 'homepage/index.html', context)


def add_log(request):

    if request.method == 'POST':
        form = AddLog(request.POST)
        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/index')
    else:
        form = AddLog()

    context = {
        'form':form,

    }

    return render(request, 'homepage/add_log.html', context)

class AddLog(forms.Form):
    TIME_CHOICES = (
        ('9:00', '9:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('1:00', '1:00'),
        ('2:00', '2:00'),
        ('3:00', '3:00'),
        ('4:00', '4:00'),
        ('5:00', '5:00'),
        ('6:00', '6:00'),
    )

    visit_description = forms.CharField(label="Visit Description", required=True, max_length=1000, widget=forms.TextInput(attrs={'placeholder':'Please describe your visit.'}))
    next_steps = forms.CharField(label="Next Steps", required=True, max_length=250, widget=forms.TextInput(attrs={'placeholder':'Describe what you plan to do next.'}))
    time_of_visit = forms.ChoiceField(label="Time Of Visit", choices=TIME_CHOICES, required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddLog, self).__init__(*args, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def commit(self, user):
        log = mod.Log()
        log.date_created = datetime.now()
        log.visit_description = self.cleaned_data.get('visit_description')
        log.next_steps = self.cleaned_data.get('next_steps')
        log.time_of_visit = self.cleaned_data.get('time_of_visit')
        log.intern = mod.Intern.objects.get(username = 'jvclapier') # TODO: Update to dynamically populate
        log.client = mod.Client.objects.get(first_name = 'Zaldy') #TODO Update to dynamically populate
        log.save()
