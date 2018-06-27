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
@login_required(login_url = '/login/')
def index(request):
    current_user = request.user

    clients = mod.Client.objects.all()

    context = {
        'clients':clients,
        'current_user': current_user,
    }

    return render(request, 'homepage/index.html', context)


def login(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/index')
    else:
        form = LoginForm()


    context = {
        'form': form,
    }

    return render(request, 'homepage/login.html', context)

class LoginForm(forms.Form):
    username = forms.CharField(label="", required=True, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Username', 'class':'form-control'}))
    password = forms.CharField(label="", required=True, widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-control'}))

    def clean(self):
        cleaned_data = super().clean()

        self.user = authenticate(username=self.cleaned_data.get('username'), password=self.cleaned_data.get('password'))
        if self.user is None:
            raise forms.ValidationError('Invalid Username and Password.')

        return cleaned_data

    def commit(self, request):

        auth_login(request, self.user)

def logout(request):

    auth_logout(request)
    return HttpResponseRedirect('/login')

@login_required(login_url = '/login/')
def add_log(request, id):

    current_user = request.user
    current_client = mod.Client.objects.get(id=id)
    print("##### The current client is", current_client.first_name)

    if request.method == 'POST':
        form = AddLog(request.POST)
        if form.is_valid():

            form.commit(request, current_client)

            return HttpResponseRedirect('/index')
    else:
        form = AddLog()

    context = {
        'form':form,
        'current_client':current_client,

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

    def commit(self, request, current_client):
        log = mod.Log()
        log.date_created = datetime.now()
        log.visit_description = self.cleaned_data.get('visit_description')
        log.next_steps = self.cleaned_data.get('next_steps')
        log.time_of_visit = self.cleaned_data.get('time_of_visit')
        log.intern = mod.Intern.objects.get(id = request.user.id)
        log.client = mod.Client.objects.get(id = current_client.id)
        log.save()

        print('##### log.intern =', log.intern.first_name)
        print('##### log.client =', log.client.first_name)


def client_profile(request, id):

    current_client = mod.Client.objects.get(id=id)

    context = {
    'current_client':current_client,
    }

    return render(request, 'homepage/client_profile.html', context)
