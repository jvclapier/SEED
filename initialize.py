import os, os.path, sys
from django.core import management
from django.db import connection
from datetime import date, datetime


# ensure the user really wants to do this
areyousure = input('''
  You are about to drop and recreate the entire database.
  All data are about to be deleted.  Use of this script
  may cause itching, vertigo, dizziness, tingling in
  extremities, loss of balance or coordination, slurred
  speech, temporary zoobie syndrome, longer lines at the
  testing center, changed passwords in Learning Suite, or
  uncertainty about whether to call your professor
  'Brother' or 'Doctor'.

  Please type 'yes' to confirm the data destruction: ''')
if areyousure.lower() != 'yes':
    print()
    print('  Wise choice.')
    sys.exit(1)

# initialize the django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'seedsite.settings'
import django
from django.conf import settings as django_settings
django.setup()


# drop and recreate the database tables
print()
print('Living on the edge!  Dropping the current database tables.')
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE")
    cursor.execute("CREATE SCHEMA public")
    cursor.execute("GRANT ALL ON SCHEMA public TO postgres")
    cursor.execute("GRANT ALL ON SCHEMA public TO public")

# make the migrations and migrate
management.call_command('makemigrations')
management.call_command('migrate')

#imports for our project
from homepage import models as mod
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

# List all current permissions
# for p in Permission.objects.all():
#     print(p.codename)

# Change color for print statements
W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
#Example Print Statement: print(R + '\nQuery 3: Prints all female users\n' + W)

'''create permission'''
def CreatePermission(content_type, codename, name):
    content_type = ContentType.objects.get_for_model(content_type)
    permission = Permission.objects.create(
    codename=codename,
    name=name,
    content_type=content_type,
    )
    print(R + '>>>>> Created Permission: ', codename + W)

'''initialize permissions'''
CreatePermission(mod.Intern, 'admin_portal', 'Administrator Permission')
CreatePermission(mod.Intern, 'intern_portal', 'Intern Permission')


'''create group'''
def CreateGroup(name, permissions):
    group = Group()
    group.name = name
    group.save()
    for permission in permissions:
        group.permissions.add(Permission.objects.get(codename=permission))
    group.save()
    print(R + '>>>>> Created Group:', name + W)

'''Initialize Groups'''
CreateGroup('Admins', permissions = ['admin_portal'])
CreateGroup('Interns', permissions = ['intern_portal'])

admin = mod.Intern()
admin.first_name = 'Andy'
admin.last_name = 'Thunell'
admin.email = 'andy.thunell@usu.edu'
admin.semester = ''
admin.username = 'andy.thunell@usu.edu'
admin.location = ''
admin.set_password(django_settings.ADMIN_PASSWORD)
admin.save()
admin_group = Group.objects.get(name='Admins')
admin_group.user_set.add(admin)
