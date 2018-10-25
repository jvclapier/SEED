'''
This view operates as a router. If a user has never logged in, they
will be redirected to the edit profile page. Next it checks their
permissions and redirects them to the proper portal.
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
