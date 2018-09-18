'''
This app deals with any action relating to clients. This includes
creating a client profile, viewing a client profile, editing a
client profile, deleting a client, and viewing all inactive clients.
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


# This function directs users to the AddClient form, allowing them to add a new client to the database.
# After adding the new client to the database, users are redirected to the index page.
@login_required(login_url = '/login/')
def add_client(request):
    if request.method == 'POST':
        form = siteForms.AddClient(request.POST)

        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/index/')
    else:
        form = siteForms.AddClient()

    context = {
    'form':form,
    }

    return render(request, 'homepage/add_client.html', context)

# This function finds the client ID, finds all logs concerning that client, and directs the user to the client_profile page
@login_required(login_url = '/login/')
def client_profile(request, id):

    current_client = mod.Client.objects.get(id=id)
    client_logs = mod.Log.objects.filter(client=current_client).order_by('-date_visited')

    context = {
    'current_client':current_client,
    'client_logs':client_logs,
    }

    return render(request, 'homepage/client_profile.html', context)

# This function finds the current client ID and directs the user to the EditClient form.
# It also autofills the form with any information that is already recorded in the database.
@login_required(login_url = '/login/')
def edit_client(request, id):

    current_client = mod.Client.objects.get(id=id)
    print("##### The current client is", current_client.first_name)

    if request.method == 'POST':
        form = siteForms.EditClient(request.POST)
        if form.is_valid():

            form.commit(request, current_client)

            return HttpResponseRedirect('/index/')
    else:
        form = siteForms.EditClient({'first_name':current_client.first_name,
            'last_name':current_client.last_name, 'gender': current_client.gender,
            'email':current_client.email, 'phone_number': current_client.phone_number,
            'language': current_client.language, 'literacy': current_client.literacy, 'location': current_client.location,
            'lat': current_client.lat, 'lon':current_client.lon,
            'business_name': current_client.business_name, 'business_type': current_client.business_type,
            'transportation_method': current_client.transportation_method, 'bio': current_client.bio,

        })

    context = {
        'form':form,
        'current_client':current_client,

    }

    return render(request, 'homepage/edit_client.html', context)

# Toggles the activity status of a client. To users, it seems like the
# client is being deleted.
def delete_client(request, id):

    current_client = mod.Client.objects.get(id=id)
    if current_client.active == True:
        current_client.active = False
        current_client.save()
    elif current_client.active == False:
        current_client.active = True
        current_client.save()

    return HttpResponseRedirect('/index/')

# Showing the user all clients that have been marked as inactive.
def inactive_clients(request):

    current_user = request.user
    inactive_assigned = mod.Client.objects.filter(active=False, assignedclient__intern = current_user).order_by('first_name')
    inactive_unassigned = mod.Client.objects.filter(active=False).exclude(assignedclient__intern = current_user).order_by('first_name')

    context = {
        'inactive_assigned': inactive_assigned,
        'inactive_unassigned':inactive_unassigned
    }

    return render(request, 'homepage/inactive_clients.html', context)
