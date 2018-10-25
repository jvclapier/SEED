'''
This view contains all forms used in the website.
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
from datetime import datetime
from homepage import models as mod

# Resources used by multiple forms

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

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

LOCATION = (
    ('',''),
    ('Philippines', 'Philippines'),
    ('Trujillo', 'Trujillo'),
    ('Lima', 'Lima'),
    ('DR', 'DR'),
    ('Ghana', 'Ghana'),
)

SEMESTER = (
    ('',''),
    ('Summer', 'Summer'),
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
)

LITERACY = (
    ('',''),
    ('Poor', 'Poor'),
    ('Adequate', 'Adequate'),
    ('Proficient', 'Proficient'),
)

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

# This form records a visit description, details about next steps, and time of visit.
class AddLog(forms.Form):

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

# This form updates information about a client.
# The fields will autofill with existing information allowing users to update them with new information.
class EditClient(forms.Form):

    LOCATION = (
        ('',''),
        ('Philippines', 'Philippines'),
        ('Trujillo', 'Trujillo'),
        ('Lima', 'Lima'),
        ('DR', 'DR'),
        ('Ghana', 'Ghana'),
    )

    first_name = forms.CharField(label="First Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number', 'class':'form-control'}))
    language = forms.CharField(label="Language", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Language', 'class':'form-control'}))
    literacy = forms.ChoiceField(label="Literacy", choices=LITERACY, required=False)
    lat = forms.CharField(label="Latitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Latitude', 'class':'form-control', 'class':'form-control'}))
    lon = forms.CharField(label="Longitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Longitude', 'class':'form-control', 'class':'form-control'}))
    business_name = forms.CharField(label="Business Name", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Name', 'class':'form-control', 'class':'form-control'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Type', 'class':'form-control', 'class':'form-control'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=100, widget=forms.Textarea(attrs={'placeholder':'Please describe how you got there', 'class':'form-control', 'class':'form-control', 'width':'100%', 'rows':'3'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client', 'class':'form-control', 'class':'form-control', 'width':'100%', 'rows':'4'}))


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
        client.language = self.cleaned_data.get('language')
        client.literacy = self.cleaned_data.get('literacy')
        client.year = self.cleaned_data.get('year')
        client.lat = self.cleaned_data.get('lat')
        client.lon = self.cleaned_data.get('lon')
        client.business_name = self.cleaned_data.get('business_name')
        client.business_type = self.cleaned_data.get('business_type')
        client.transportation_method = self.cleaned_data.get('transportation_method')
        client.bio = self.cleaned_data.get('bio')
        client.save()

        print('##### client.first_name =', client.first_name)

# This form allows users to enter new clients into the database.
class AddClient(forms.Form):

    image = forms.ImageField(label="Client Image", required=True)
    first_name = forms.CharField(label="First Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=True, max_length=12, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    gender = forms.ChoiceField(label="Client Gender", choices=GENDER_CHOICES, required=False)
    email = forms.CharField(label="Email Address", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    phone_number = forms.CharField(label="Phone Number", required=False, max_length=11, widget=forms.TextInput(attrs={'placeholder':'Phone Number', 'class':'form-control'}))
    language = forms.CharField(label="Language", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Language', 'class':'form-control'}))
    literacy = forms.ChoiceField(label="Literacy", choices=LITERACY, required=False)
    organization = forms.CharField(label="Organization", required=False, max_length=25, widget=forms.TextInput(attrs={'placeholder':'Organization', 'class':'form-control'}))
    lat = forms.CharField(label="Latitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Latitude', 'class':'form-control'}))
    lon = forms.CharField(label="Longitude", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Longitude', 'class':'form-control'}))
    business_name = forms.CharField(label="Business Name", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Name', 'class':'form-control'}))
    business_type = forms.CharField(label="Business Type", required=False, max_length=20, widget=forms.TextInput(attrs={'placeholder':'Business Type', 'class':'form-control'}))
    transportation_method = forms.CharField(label="Transportation Method", required=False, max_length=100, widget=forms.Textarea(attrs={'placeholder':'Please describe how you got there', 'class':'form-control', 'width':'100%', 'rows':'3'}))
    bio = forms.CharField(label="Client Bio", required=False, max_length=1000, widget=forms.Textarea(attrs={'placeholder':'Write a brief bio about your overall experience with this client', 'class':'form-control', 'width':'100%', 'rows':'4'}))


    def __init__(self, *arg, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddClient, self).__init__(*arg, **kwargs)
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def commit(self, request):
        client = mod.Client()
        client.image = self.cleaned_data.get('image')
        client.first_name = self.cleaned_data.get('first_name')
        client.last_name = self.cleaned_data.get('last_name')
        client.gender = self.cleaned_data.get('gender')
        client.email = self.cleaned_data.get('email')
        client.phone_number = self.cleaned_data.get('phone_number')
        client.language = self.cleaned_data.get('language')
        client.literacy = self.cleaned_data.get('literacy')
        client.organization = self.cleaned_data.get('organization')
        client.semester = request.user.semester
        client.year = request.user.year
        client.location = request.user.location
        client.lat = self.cleaned_data.get('lat')
        client.lon = self.cleaned_data.get('lon')
        client.business_name = self.cleaned_data.get('business_name')
        client.business_type = self.cleaned_data.get('business_type')
        client.transportation_method = self.cleaned_data.get('transportation_method')
        client.bio = self.cleaned_data.get('bio')
        client.save()

        print('##### client.first_name =', client.first_name)

# This form allows someone with administrator permission to edit an intern profile
class AdminEditProfile(forms.Form):

    PERMISSIONS = (
        ('intern_portal', 'Intern'),
        ('admin_portal', 'Admin'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    email = forms.CharField(label="Email Address", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    semester = forms.ChoiceField(label="Semester", choices=SEMESTER, required=False)
    year = forms.CharField(label="Year", required=False, max_length=4, widget=forms.TextInput(attrs={'placeholder':'YYYY', 'class':'form-control'}))
    location = forms.ChoiceField(label="Location", choices=LOCATION, required=True)
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

# This form allows administrators to create new interns
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

    LOCATION = (
        ('',''),
        ('Philippines', 'Philippines'),
        ('Trujillo', 'Trujillo'),
        ('Lima', 'Lima'),
        ('DR', 'DR'),
        ('Ghana', 'Ghana'),
    )

    first_name = forms.CharField(label="First Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'First Name', 'class':'form-control'}))
    last_name = forms.CharField(label="Last Name", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Last Name', 'class':'form-control'}))
    email = forms.CharField(label="Email Address", required=False, max_length=50, widget=forms.TextInput(attrs={'placeholder':'Email Address', 'class':'form-control'}))
    password = forms.CharField(label="Password", required=False, max_length=100, widget=forms.PasswordInput(attrs={'placeholder':'Password', 'class':'form-control'}))
    semester = forms.ChoiceField(label="Semester", choices=SEMESTER, required=True)
    location = forms.ChoiceField(label="Location", choices=LOCATION, required=True)
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
        intern.location = self.cleaned_data.get('location')
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

# This form allows users to edit their own profile
class EditProfile(forms.Form):

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
