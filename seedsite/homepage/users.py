'''
This app deals with all user information. It creates the admin portal and
allows the admin to add and edit users (interns). It also creates the intern
portal, allowing interns to view clients, edit their own profile, bookmark
clients, and log visits with clients.
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

@login_required(login_url = '/login/')
@permission_required('homepage.admin_portal')
def add_intern(request):

    if request.method == 'POST':
        form = siteForms.AddIntern(request.POST)
        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/admin_portal/')
    else:
        form = siteForms.AddIntern()

    context = {
        'form':form,
    }

    return render(request, 'homepage/add_intern.html', context)

@login_required(login_url = '/login/')
def edit_profile(request):

    current_user = request.user

    if request.method == 'POST':
        form = siteForms.EditProfile(request.POST, request=request)
        if form.is_valid():

            form.commit(request, current_user)

            return HttpResponseRedirect('/index/')
    else:
        form = siteForms.EditProfile({'first_name':current_user.first_name, 'last_name':current_user.last_name,
            'email':current_user.email, 'semester':current_user.semester, 'year':current_user.year
        })

    context = {
        'form':form,
        'current_user':current_user,
    }

    return render(request, 'homepage/edit_profile.html', context)

@login_required(login_url = '/login/')
@permission_required('homepage.admin_portal')
def admin_edit_profile(request, id):

    selected_intern = mod.Intern.objects.get(id=id)

    if request.method == 'POST':
        form = siteForms.AdminEditProfile(request.POST, request=request)
        if form.is_valid():

            form.commit(request, selected_intern)

            return HttpResponseRedirect('/admin_portal/')
    else:
        form = siteForms.AdminEditProfile({'first_name':selected_intern.first_name, 'last_name':selected_intern.last_name,
            'email':selected_intern.email, 'location':selected_intern.location, 'semester':selected_intern.semester, 'year':selected_intern.year, 'permissions':get_current_group(selected_intern),
        })

    context = {
        'form':form,
        'selected_intern':selected_intern,
    }

    return render(request, 'homepage/admin_edit_profile.html', context)

@login_required(login_url = '/login/')
def intern_portal(request):

    current_user = request.user
    assigned_clients_ordered = mod.Client.objects.filter(active = True, location = current_user.location, assignedclient__intern = current_user).order_by('first_name')
    unassigned_clients = mod.Client.objects.filter(active = True, location = current_user.location).exclude(assignedclient__intern = current_user).order_by('first_name')

    context = {
        'assigned_clients_ordered':assigned_clients_ordered,
        'unassigned_clients':unassigned_clients,
        'current_user': current_user,
    }

    return render(request, 'homepage/intern_portal.html', context)

@login_required(login_url = '/login/')
@permission_required('homepage.admin_portal', login_url='/index/')
def admin_portal(request):

    current_user = request.user
    interns = mod.Intern.objects.filter(groups__name='Interns').filter(is_active = True).order_by('-date_joined')
    assigned_clients = mod.AssignedClient.objects.all().prefetch_related('intern', 'client')

    context = {
        'current_user':current_user,
        'interns':interns,
        'assigned_clients':assigned_clients,
    }

    return render(request, 'homepage/admin_portal.html', context)

@login_required(login_url = '/login/')
def add_bookmark(request, id):
    # initialize variables
    current_user = request.user
    current_client = mod.Client.objects.get(id=id)
    print('#### Add bookmark funciton called')
    bookmark_exists = False
    existing_bookmark = None

    # check to see if the selected client is is_active
    if current_client.active == False:
        current_client.active = True
        current_client.save()

    # check to see if clients and intern have an object in AssignedClient
    all_assigned_clients = mod.AssignedClient.objects.all()
    for item in all_assigned_clients:
        if ((item.client == current_client) and (item.intern == current_user)):
            bookmark_exists = True
            existing_bookmark = item

    # use bookmark status to delete or create assigned client object
    if bookmark_exists == True:
        # if the bookmark exists delete bookmark
        mod.AssignedClient.objects.get(id=existing_bookmark.id).delete()
    else:
        #if the bookmark does not exist, create bookmark
        new_assigned_client = mod.AssignedClient()
        new_assigned_client.intern = current_user
        new_assigned_client.client = current_client
        new_assigned_client.save()

    return HttpResponseRedirect('/index/')

def get_current_group(selected_intern):
    current_group = None
    if selected_intern.groups.filter(name='Interns').exists():
        current_group = 'intern_portal'
    elif selected_intern.groups.filter(name='Admins').exists():
        current_group = 'admin_portal'
    return current_group

# toggling between an active and inactive client
@permission_required('homepage.admin_portal')
@login_required(login_url = '/login/')
def deactivate_intern(request, id):

    current_intern = mod.Intern.objects.get(id=id)
    if current_intern.is_active == True:
        current_intern.is_active = False
        current_intern.save()
    elif current_intern.is_active == False:
        current_intern.is_active = True
        current_intern.save()

    return HttpResponseRedirect('/index/')

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
