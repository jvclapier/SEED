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
from django.db.models import Q

@login_required(login_url = '/login/')
def index(request):
    #initialize variables
    current_user = request.user
    all_clients = mod.Client.objects.all().order_by('first_name')
    assigned_client_objects = mod.AssignedClient.objects.filter(intern = current_user)
    assigned_clients = []
    assigned_clients_ordered = []
    unassigned_clients = []
    # Loop through the assigned clients and add each to the assigned clients list
    for item in assigned_client_objects:
        client_to_add = mod.Client.objects.get(id = item.client.id)
        assigned_clients.append(client_to_add)
    # Looping through the all clients list to order the assigned client list
    for item in all_clients:
        for i in assigned_clients:
            if item == i:
                assigned_clients_ordered.append(item)
            else:
                continue
    # Loop through the all clients list
    for item in all_clients:
        client_exists = False
        # Loop through the assigned clients list to see if the client exists.
        # If the client does not exist, add it to the unassigned client list
        for i in assigned_clients:
            if item == i:
                client_exists = True
            else:
                continue
        if client_exists == False:
            unassigned_clients.append(item)
        else:
            continue

    context = {
        'assigned_clients_ordered':assigned_clients_ordered,
        'unassigned_clients':unassigned_clients,
        'current_user': current_user,
    }

    return render(request, 'homepage/index.html', context)

# This directs users to the login form. Once they have successfully logged in, it sends them to the index page.
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

# This form takes a user's username and password, validates and authenticates it, and logs the user into the site.
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


# This function logs the user out of the website adn redirects them to the login page.
@login_required(login_url = '/login/')
def logout(request):

    auth_logout(request)
    return HttpResponseRedirect('/login')


# This function takes the current user and current client and directs the user to the AddLog form.
# If the request is a post, the function commits the form data and redirects the user to the index page.
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


# This form records a visit description, details about next steps, and time of visit.
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

    visit_description = forms.CharField(label="Visit Description", required=True, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Please describe your visit.'}))
    next_steps = forms.CharField(label="Next Steps", required=True, max_length=250, widget=forms.Textarea(attrs={'placeholder':'Describe what you plan to do next.'}))
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

# This function finds the client ID, finds all logs concerning that client, and directs the user to the client_profile page
@login_required(login_url = '/login/')
def client_profile(request, id):

    current_client = mod.Client.objects.get(id=id)
    client_logs = mod.Log.objects.filter(client=current_client)

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
        form = EditClient(request.POST)
        if form.is_valid():

            form.commit(request, current_client)

            return HttpResponseRedirect('/client_profile/'+str(id))
    else:
        form = EditClient({'first_name':current_client.first_name,
            'last_name':current_client.last_name, 'gender': current_client.gender,
            'email':current_client.email, 'phone_number': current_client.phone_number,
            'tagalog_needed': current_client.tagalog_needed, 'street_address': current_client.street_address,
            'city': current_client.city, 'zipcode': current_client.zipcode, 'country': current_client.country,
            'barangay': current_client.barangay, 'business_name': current_client.business_name,
            'business_type': current_client.business_type, 'transportation_method': current_client.transportation_method,
            'bio': current_client.bio,

        })

    context = {
        'form':form,
        'current_client':current_client,

    }

    return render(request, 'homepage/edit_client.html', context)

# This form updates information about a client.
# The fields will autofill with existing information allowing users to update them with new information.
class EditClient(forms.Form):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number'}))
    tagalog_needed = forms.BooleanField(label="Tagalog Needed", required=False, initial=False)
    street_address = forms.CharField(label="Street Address", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Street Address'}))
    city = forms.CharField(label="City", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'City'}))
    zipcode = forms.CharField(label="Zipcode", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Zipcode'}))
    country = forms.CharField(label="Country", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Country'}))
    barangay = forms.CharField(label="Barangay", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Barangay'}))
    ## TODO: Create google maps API
    business_name = forms.CharField(label="Business Name", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Business Name'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Business Type'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=500, widget=forms.TextInput(attrs={'placeholder':'Please describe how you got there'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client'}))


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditClient, self).__init__(*args, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def commit(self, request, current_client):
        client = current_client
        client.first_name = self.cleaned_data.get('first_name')
        client.last_name = self.cleaned_data.get('last_name')
        client.gender = self.cleaned_data.get('gender')
        client.email = self.cleaned_data.get('email')
        client.phone_number = self.cleaned_data.get('phone_number')
        client.tagalog_needed = self.cleaned_data.get('tagalog_needed')
        client.street_address = self.cleaned_data.get('street_address')
        client.city = self.cleaned_data.get('city')
        client.zipcode = self.cleaned_data.get('zipcode')
        client.country = self.cleaned_data.get('country')
        client.barangay = self.cleaned_data.get('barangay')
        client.business_name = self.cleaned_data.get('business_name')
        client.business_type = self.cleaned_data.get('business_type')
        client.transportation_method = self.cleaned_data.get('transportation_method')
        client.bio = self.cleaned_data.get('bio')
        client.save()

        print('##### client.first_name =', client.first_name)

# This function directs users to the AddClient form, allowing them to add a new client to the database.
# After adding the new client to the database, users are redirected to the index page.
@login_required(login_url = '/login/')
def add_client(request):
    if request.method == 'POST':
        form = AddClient(request.POST)

        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/index/')
    else:
        form = AddClient()

    context = {
    'form':form,
    }

    return render(request, 'homepage/add_client.html', context)

# This form allows users to enter new clients into the database.
class AddClient(forms.Form):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=True, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number'}))
    tagalog_needed = forms.BooleanField(label="Tagalog Needed", required=False, initial=False)
    street_address = forms.CharField(label="Street Address", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Street Address'}))
    city = forms.CharField(label="City", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'City'}))
    zipcode = forms.CharField(label="Zipcode", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Zipcode'}))
    country = forms.CharField(label="Country", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Country'}))
    barangay = forms.CharField(label="Barangay", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Barangay'}))
    ## TODO: Create google maps API
    business_name = forms.CharField(label="Business Name", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Business Name'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Business Type'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=500, widget=forms.TextInput(attrs={'placeholder':'Please describe how you got there'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client'}))


    def __init__(self, *arg, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddClient, self).__init__(*arg, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def commit(self, request):
        client = mod.Client()
        client.first_name = self.cleaned_data.get('first_name')
        client.last_name = self.cleaned_data.get('last_name')
        client.gender = self.cleaned_data.get('gender')
        client.email = self.cleaned_data.get('email')
        client.phone_number = self.cleaned_data.get('phone_number')
        client.tagalog_needed = self.cleaned_data.get('tagalog_needed')
        client.street_address = self.cleaned_data.get('street_address')
        client.city = self.cleaned_data.get('city')
        client.zipcode = self.cleaned_data.get('zipcode')
        client.country = self.cleaned_data.get('country')
        client.barangay = self.cleaned_data.get('barangay')
        client.business_name = self.cleaned_data.get('business_name')
        client.business_type = self.cleaned_data.get('business_type')
        client.transportation_method = self.cleaned_data.get('transportation_method')
        client.bio = self.cleaned_data.get('bio')
        client.save()

        print('##### client.first_name =', client.first_name)

# This takes a user input to search current clients in the database. Users can search for a client based on first name,
# last name, or busienss name. It returns a list of clients ordered by the client's first name.
@login_required(login_url = '/login/')
def search(request):
    current_user = request.user
    user_input = request.GET.get('client_name')
    if user_input is None:
        return HttpResponseRedirect('/index/')

    filtered_clients = mod.Client.objects.filter(Q(first_name__icontains=user_input) | Q(last_name__icontains=user_input) | Q(business_name__icontains=user_input)).order_by('first_name')
    assigned_client_objects = mod.AssignedClient.objects.filter(intern = current_user).order_by('client')
    assigned_clients_filtered = []
    unassigned_clients_filtered = []
    for item in assigned_client_objects:
        for i in filtered_clients:
            if item.client == i:
                assigned_clients_filtered.append(i)
    for item in filtered_clients:
        client_exists = False
        for i in assigned_clients_filtered:
            if item == i:
                client_exists = True
            else:
                continue
        if client_exists == False:
            unassigned_clients_filtered.append(item)
        else:
            continue

    context = {
        'assigned_clients_filtered':assigned_clients_filtered,
        'unassigned_clients_filtered':unassigned_clients_filtered,
        'current_user': current_user,
    }

    return render(request, 'homepage/search.html', context)

@login_required(login_url = '/login/')
def add_bookmark(request, id):
    # initialize variables
    current_user = request.user
    current_client = mod.Client.objects.get(id=id)
    print('#### Add bookmark funciton called')
    bookmark_exists = False
    existing_bookmark = None

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

@login_required(login_url = '/login/')
def intern_portal(request):

    current_user = request.user

    context = {
        'current_user':current_user,
    }

    return render(request, 'homepage/intern_portal.html', context)
