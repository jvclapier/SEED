'''
This view deals with all authentication of users. This includes both logging in and
logging out.
'''

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime
import re
from django.template.loader import render_to_string, get_template
from django.conf import settings as django_settings
from homepage import models as mod
from django.db.models import Q
from django.contrib.auth.models import Permission, Group
from homepage import siteForms
from django.contrib.auth.models import Permission, Group

# This directs users to the login form. Once they have successfully logged in, it sends them to the index page.
def login(request):

    if request.method == 'POST':
        form = siteForms.LoginForm(request.POST)
        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/index')
    else:
        form = siteForms.LoginForm()


    context = {
        'form': form,
    }

    return render(request, 'homepage/login.html', context)

# This function logs the user out of the website adn redirects them to the login page.
@login_required(login_url = '/login/')
def logout(request):

    auth_logout(request)
    return HttpResponseRedirect('/login')
