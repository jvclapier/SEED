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
from django.core.mail import send_mail
import re
from django.template.loader import render_to_string, get_template
from django.conf import settings as django_settings
from homepage import models as mod
from django.db.models import Q
from django.contrib.auth.models import Permission, Group

# use index to route based on user permission
@login_required(login_url = '/login/')
def index(request):

    current_user = request.user
    # prompt user to change password if on first login
    if current_user.is_previously_logged_in == False:
        return HttpResponseRedirect('/edit_profile')
    # run different logic depending on logged in user type
    elif current_user.has_perm('homepage.admin_portal'):
        return HttpResponseRedirect('/admin_portal')
    elif current_user.has_perm('homepage.intern_portal'):
        return HttpResponseRedirect('/intern_portal')

@login_required(login_url = '/login/')
def intern_portal(request):

    current_user = request.user
    all_clients = mod.Client.objects.filter(active = True).order_by('first_name')
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

    return render(request, 'homepage/intern_portal.html', context)


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

    visit_description = forms.CharField(label="Visit Description", required=True, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Please describe your visit', 'class':'form-control'}))
    next_steps = forms.CharField(label="Next Steps", required=True, max_length=250, widget=forms.Textarea(attrs={'placeholder':'Describe what you plan to do next', 'class':'form-control'}))
    date_visited = forms.DateField(label="Date Visited", required=True, widget=forms.DateInput(format='%m/%d/%Y', attrs={'placeholder':'MM/DD/YYYY', 'class':'form-control'}))
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
        log.date_visited = self.cleaned_data.get('date_visited')
        log.intern = mod.Intern.objects.get(id = request.user.id)
        log.client = mod.Client.objects.get(id = current_client.id)
        log.save()

        print('##### log.intern =', log.intern.first_name)
        print('##### log.client =', log.client.first_name)

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
        form = EditClient(request.POST)
        if form.is_valid():

            form.commit(request, current_client)

            return HttpResponseRedirect('/index/')
    else:
        form = EditClient({'first_name':current_client.first_name,
            'last_name':current_client.last_name, 'gender': current_client.gender,
            'email':current_client.email, 'phone_number': current_client.phone_number,
            'tagalog_needed': current_client.tagalog_needed, 'street_address': current_client.street_address,
            'city': current_client.city, 'zipcode': current_client.zipcode, 'country': current_client.country,
            'barangay': current_client.barangay, 'lat': current_client.lat, 'lon':current_client.lon,
            'business_name': current_client.business_name, 'business_type': current_client.business_type,
            'transportation_method': current_client.transportation_method, 'bio': current_client.bio,

        })

    context = {
        'form':form,
        'current_client':current_client,

    }

    return render(request, 'homepage/edit_client.html', context)

def delete_client(request, id):

    current_client = mod.Client.objects.get(id=id)
    if current_client.active == True:
        current_client.active = False
        current_client.save()
    elif current_client.active == False:
        current_client.active = True
        current_client.save()

    return HttpResponseRedirect('/index/')

# This form updates information about a client.
# The fields will autofill with existing information allowing users to update them with new information.
class EditClient(forms.Form):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    first_name = forms.CharField(label="First Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number', 'class':'form-control'}))
    tagalog_needed = forms.BooleanField(label="Tagalog Needed", required=False, initial=False)
    street_address = forms.CharField(label="Street Address", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Street Address', 'class':'form-control', 'class':'form-control'}))
    city = forms.CharField(label="City", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'City', 'class':'form-control', 'class':'form-control'}))
    zipcode = forms.CharField(label="Zipcode", required=False, max_length=10, widget=forms.TextInput(attrs={'placeholder':'Zipcode', 'class':'form-control', 'class':'form-control'}))
    country = forms.CharField(label="Country", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Country', 'class':'form-control', 'class':'form-control'}))
    barangay = forms.CharField(label="Barangay", required=False, max_length=15, widget=forms.TextInput(attrs={'placeholder':'Barangay', 'class':'form-control', 'class':'form-control'}))
    lat = forms.CharField(label="Latitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Latitude', 'class':'form-control', 'class':'form-control'}))
    lon = forms.CharField(label="Longitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Longitude', 'class':'form-control', 'class':'form-control'}))
    business_name = forms.CharField(label="Business Name", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Name', 'class':'form-control', 'class':'form-control'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Type', 'class':'form-control', 'class':'form-control'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=100, widget=forms.Textarea(attrs={'placeholder':'Please describe how you got there', 'class':'form-control', 'class':'form-control', 'width':'100%', 'rows':'3'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client', 'class':'form-control', 'class':'form-control', 'width':'100%', 'rows':'7'}))


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
        client.lat = self.cleaned_data.get('lat')
        client.lon = self.cleaned_data.get('lon')
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

    first_name = forms.CharField(label="First Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number', 'class':'form-control'}))
    tagalog_needed = forms.BooleanField(label="Tagalog Needed", required=False, initial=False)
    street_address = forms.CharField(label="Street Address", required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder':'Street Address', 'class':'form-control'}))
    city = forms.CharField(label="City", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'City', 'class':'form-control'}))
    zipcode = forms.CharField(label="Zipcode", required=False, max_length=10, widget=forms.TextInput(attrs={'placeholder':'Zipcode', 'class':'form-control'}))
    country = forms.CharField(label="Country", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Country', 'class':'form-control'}))
    barangay = forms.CharField(label="Barangay", required=False, max_length=15, widget=forms.TextInput(attrs={'placeholder':'Barangay', 'class':'form-control'}))
    lat = forms.CharField(label="Latitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Latitude', 'class':'form-control'}))
    lon = forms.CharField(label="Longitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Longitude', 'class':'form-control'}))
    business_name = forms.CharField(label="Business Name", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Name', 'class':'form-control'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Type', 'class':'form-control'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=100, widget=forms.Textarea(attrs={'placeholder':'Please describe how you got there', 'class':'form-control', 'width':'100%', 'rows':'3'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client', 'class':'form-control', 'width':'100%', 'rows':'7'}))


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
        client.lat = self.cleaned_data.get('lat')
        client.lon = self.cleaned_data.get('lon')
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
    # intiialize variables
    current_user = request.user
    query_string = ''
    filtered_clients = None
    assigned_clients_filtered = []
    unassigned_clients_filtered = []
    if ('client_name' in request.GET) and request.GET['client_name'].strip():
        query_string = request.GET.get('client_name')
        query = get_query(query_string, ['first_name', 'last_name', 'business_name'])
        filtered_clients = mod.Client.objects.filter(query).order_by('first_name')
    assigned_client_objects = mod.AssignedClient.objects.filter(intern = current_user).order_by('client')
    # check assigned client objects to find pairs where intern exists
    for item in filtered_clients:
        for i in assigned_client_objects:
            # if intern exists in assigned client pair, add it to the assigned clients filtered list
            if item == i.client:
                assigned_clients_filtered.append(item)
    # check to see which clients have already been added to the assigned clients filtered list
    for item in filtered_clients:
        client_exists = False
        for i in assigned_clients_filtered:
            # if the intern exists, set the client_exists variable list to true
            if item == i:
                client_exists = True
            else:
                continue
        # if the client does not exist, add it to the unassigned_clients_filtered list
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
def edit_profile(request):

    current_user = request.user

    if request.method == 'POST':
        form = EditProfile(request.POST, request=request)
        if form.is_valid():

            form.commit(request, current_user)

            return HttpResponseRedirect('/index/')
    else:
        form = EditProfile({'first_name':current_user.first_name, 'last_name':current_user.last_name,
            'email':current_user.email, 'semester':current_user.semester, 'year':current_user.year
        })

    context = {
        'form':form,
        'current_user':current_user,
    }

    return render(request, 'homepage/edit_profile.html', context)


class EditProfile(forms.Form):

    SEMESTER = (
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    email = forms.CharField(label="Email Address", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    semester = forms.ChoiceField(label="Semester", choices=SEMESTER, required=False)
    current_password = forms.CharField(label="Current Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'Current Password', 'class':'form-control step'}))
    new_password = forms.CharField(label="New Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'New Password', 'class':'form-control step', 'disabled':True}))
    confirm_new_password = forms.CharField(label="Confirm New Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'Confirm New Password', 'class':'form-control step', 'disabled':True}))
    year = forms.CharField(label="Year", required=False, max_length=4, widget=forms.TextInput(attrs={'placeholder':'YYYY', 'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditProfile, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.cleaned_data.get('current_password') != '' and self.cleaned_data.get('current_password') is not None:
            temp_user = authenticate(username=self.request.user.username, password=self.cleaned_data.get('current_password'))
            if temp_user is None:
                self._errors['current_password'] = self.error_class(['Incorrect password'])

            if self.cleaned_data.get('new_password') != self.cleaned_data.get('confirm_new_password'):
                self._errors['new_password'] = self.error_class(['Passwords do not match'])

        return cleaned_data

    def commit(self, request, current_user):
        user = current_user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.semester = self.cleaned_data.get('semester')
        user.year = self.cleaned_data.get('year')
        if self.cleaned_data.get('current_password') != '' and self.cleaned_data.get('current_password') is not None:
            if self.cleaned_data.get('confirm_new_password') != '' and self.cleaned_data.get('confirm_new_password') is not None:
                user.set_password(self.cleaned_data.get('confirm_new_password'))
                user.is_previously_logged_in = True
        user.save()
        temp_user = authenticate(username=self.request.user.username, password=self.cleaned_data.get('confirm_new_password'))
        auth_login(self.request, temp_user)

def get_current_group(selected_intern):
    current_group = None
    if selected_intern.groups.filter(name='Interns').exists():
        current_group = 'intern_portal'
    elif selected_intern.groups.filter(name='Admins').exists():
        current_group = 'admin_portal'
    return current_group

@login_required(login_url = '/login/')
@permission_required('homepage.admin_portal')
def admin_edit_profile(request, id):

    selected_intern = mod.Intern.objects.get(id=id)

    if request.method == 'POST':
        form = AdminEditProfile(request.POST, request=request)
        if form.is_valid():

            form.commit(request, selected_intern)

            return HttpResponseRedirect('/admin_portal/')
    else:
        form = AdminEditProfile({'first_name':selected_intern.first_name, 'last_name':selected_intern.last_name,
            'email':selected_intern.email, 'semester':selected_intern.semester, 'year':selected_intern.year, 'permissions':get_current_group(selected_intern),
        })

    context = {
        'form':form,
        'selected_intern':selected_intern,
    }

    return render(request, 'homepage/admin_edit_profile.html', context)

class AdminEditProfile(forms.Form):

    PERMISSIONS = (
        ('intern_portal', 'Intern'),
        ('admin_portal', 'Admin'),
    )

    SEMESTER = (
        ('',''),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    email = forms.CharField(label="Email Address", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    semester = forms.ChoiceField(label="Semester", choices=SEMESTER, required=False)
    year = forms.CharField(label="Year", required=False, max_length=4, widget=forms.TextInput(attrs={'placeholder':'YYYY', 'class':'form-control'}))
    permissions = forms.ChoiceField(label="Permissions", choices=PERMISSIONS, required=True)
    new_password = forms.CharField(label="New Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'New Password', 'class':'form-control'}))
    confirm_new_password = forms.CharField(label="Confirm New Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'Confirm New Password', 'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AdminEditProfile, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.cleaned_data.get('new_password') != self.cleaned_data.get('confirm_new_password'):
            self._errors['new_password'] = self.error_class(['Passwords do not match'])

        return cleaned_data

    def commit(self, request, selected_intern):
        user = selected_intern
        current_group = 'Interns' if get_current_group(user) == 'intern_portal'  else 'Admins'
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.semester = self.cleaned_data.get('semester')
        user.year = self.cleaned_data.get('year')
        if self.cleaned_data.get('confirm_new_password') != '' and self.cleaned_data.get('confirm_new_password') is not None:
            user.set_password(self.cleaned_data.get('confirm_new_password'))
            user.is_previously_logged_in = False
        user.save()
        if current_group != self.cleaned_data.get('permissions'):
            old_group = Group.objects.get(name=current_group)
            old_group.user_set.remove(user)
            new_group_name = 'Interns' if self.cleaned_data.get('permissions') == 'intern_portal' else 'Admins'
            new_group = Group.objects.get(name=new_group_name)
            new_group.user_set.add(user)

@login_required(login_url = '/login/')
@permission_required('homepage.admin_portal')
def add_intern(request):

    if request.method == 'POST':
        form = AddIntern(request.POST)
        if form.is_valid():

            form.commit(request)

            return HttpResponseRedirect('/admin_portal/')
    else:
        form = AddIntern()

    context = {
        'form':form,
    }

    return render(request, 'homepage/add_intern.html', context)

class AddIntern(forms.Form):

    PERMISSIONS = (
        ('intern_portal', 'Intern'),
        ('admin_portal', 'Admin'),
    )

    SEMESTER = (
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
        ('Spring', 'Spring'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    email = forms.CharField(label="Email Address", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    password = forms.CharField(label="Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-control'}))
    semester = forms.ChoiceField(label="Semester", choices=SEMESTER, required=True)
    year = forms.CharField(label="Year", required=False, max_length=4, widget=forms.TextInput(attrs={'placeholder':'YYYY', 'class':'form-control'}))
    permissions = forms.ChoiceField(label="Permissions", choices=PERMISSIONS, required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddIntern, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def commit(self, request):
        intern = mod.Intern()
        intern.first_name = self.cleaned_data.get('first_name')
        intern.last_name = self.cleaned_data.get('last_name')
        intern.email = self.cleaned_data.get('email')
        intern.semester = self.cleaned_data.get('semester')
        intern.year = self.cleaned_data.get('year')
        intern.username = self.cleaned_data.get('email')
        intern.set_password(self.cleaned_data.get('password'))
        intern.save()
        # add to group based on permission
        if self.cleaned_data.get('permissions') == 'admin_portal':
            admin_group = Group.objects.get(name='Admins')
            admin_group.user_set.add(intern)
        elif self.cleaned_data.get('permissions') == 'intern_portal':
            intern_group = Group.objects.get(name='Interns')
            intern_group.user_set.add(intern)

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
