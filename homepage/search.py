'''
This view deals with all searches done on the site. This incluedes
both searching clients and searching interns.
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

# This takes a user input to search current clients in the database. Users can search for a client based on first name,
# last name, or busienss name. It returns a list of clients ordered by the client's first name.
@login_required(login_url = '/login/')
def search(request):
    # intiialize variables
    current_user = request.user
    query_string = ''
    assigned_clients_filtered = None
    unassigned_clients_filtered = None
    if ('client_name' in request.GET) and request.GET['client_name'].strip():
        query_string = request.GET.get('client_name')
        query = get_query(query_string, ['first_name', 'last_name', 'business_name', 'semester', 'year'])
        if current_user.has_perm('homepage.admin_portal'):
            assigned_clients_filtered = mod.Client.objects.filter(query, assignedclient__intern = current_user).order_by('first_name')
            unassigned_clients_filtered = mod.Client.objects.filter(query).exclude(assignedclient__intern = current_user).order_by('first_name')
        else:
            assigned_clients_filtered = mod.Client.objects.filter(query, assignedclient__intern = current_user, location = current_user.location).order_by('first_name')
            unassigned_clients_filtered = mod.Client.objects.filter(query, location = current_user.location).exclude(assignedclient__intern = current_user).order_by('first_name')
    context = {
        'assigned_clients_filtered':assigned_clients_filtered,
        'unassigned_clients_filtered':unassigned_clients_filtered,
        'current_user': current_user,
    }

    return render(request, 'homepage/search.html', context)

@permission_required('homepage.admin_portal')
@login_required(login_url = '/login/')
def search_interns(request):
    query_string = ''
    filtered_interns = None
    if ('intern_name' in request.GET) and request.GET['intern_name'].strip():
        assigned_clients = mod.AssignedClient.objects.all().prefetch_related('intern', 'client')
        query_string = request.GET['intern_name']
        entry_query = get_query(query_string, ['first_name', 'last_name', 'semester', 'year', 'email'])
        filtered_interns = mod.Intern.objects.filter(entry_query).order_by('-date_joined')

    context = {
        'filtered_interns':filtered_interns,
        'assigned_clients':assigned_clients
    }

    return render(request, 'homepage/search_interns.html', context)

# splits strings up into individual terms
def normalize_query(query_string):
    normalized_query = query_string.split(' ')
    return normalized_query

# building a query using the specified search fields and the normalized query
def get_query(query_string, search_fields):
    query = None # final search query
    terms = normalize_query(query_string)
    for term in terms:
        temp_query = None # query to search for each term in each field
        for field_name in search_fields:
            part = Q(**{"%s__icontains" % field_name: term})
            if temp_query is None:
                temp_query = part
            else:
                temp_query = temp_query | part
        if query is None:
            query = temp_query
        else:
            query = query & temp_query
    return query
