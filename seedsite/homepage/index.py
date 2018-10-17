'''
This view operates as a router. If a user has never logged in, they
will be redirected to the edit profile page. Next it checks their
permissions and redirects them to the proper portal.
'''

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
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
