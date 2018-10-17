'''
This view allows users to log visits with clients. It works wit the AddLog
form on the forms app.
'''

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings as django_settings
from homepage import models as mod
from django.contrib.auth.models import Permission, Group
from homepage import siteForms

# This function takes the current user and current client and directs the user to the AddLog form.
# If the request is a post, the function commits the form data and redirects the user to the index page.
@login_required(login_url = '/login/')
def add_log(request, id):

    current_user = request.user
    current_client = mod.Client.objects.get(id=id)
    print("##### The current client is", current_client.first_name)

    if request.method == 'POST':
        form = siteForms.AddLog(request.POST)
        if form.is_valid():

            form.commit(request, current_client)

            return HttpResponseRedirect('/index')
    else:
        form = siteForms.AddLog()

    context = {
        'form':form,
        'current_client':current_client,

    }

    return render(request, 'homepage/add_log.html', context)
