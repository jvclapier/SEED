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
admin.first_name = 'general'
admin.last_name = 'admin'
admin.email = 'jvclapier@gmail.com'
admin.semester = ''
admin.username = 'admin'
admin.set_password(django_settings.ADMIN_PASSWORD)
admin.save()
admin_group = Group.objects.get(name='Admins')
admin_group.user_set.add(admin)

'''create interns'''
def CreateIntern(username, password, first_name, last_name, email, semester):
    intern = mod.Intern()
    intern.username = username
    intern.set_password(password)
    intern.first_name = first_name
    intern.last_name = last_name
    intern.email = email
    intern.semester = semester
    intern.save()
    print("####### Intern created: " + intern.first_name)

CreateIntern('jvclapier', 'password', 'Jessee', 'Clapier', 'jvclapier@gmail.com', 'Summer')
CreateIntern('bdsmith98', 'password', 'Benton', 'Smith', 'bdsmith98@gmail.com', 'Summer')
CreateIntern('eaglauser', 'password', 'Eliza', 'Clapier', 'eaglauser@gmail.com', 'Summer')

'''create client'''
def CreateClient(first_name, last_name, gender, email, phone_number, tagalog_needed, street_address, city, zipcode, country, barangay, business_name, business_type, transportation_method, notes):
    client = mod.Client()
    client.first_name = first_name
    client.last_name = last_name
    client.gender = gender
    client.email = email
    client.phone_number = phone_number
    client.tagalog_needed = tagalog_needed
    client.street_address = street_address
    client.city = city
    client.zipcode = zipcode
    client.country = country
    client.barangay = barangay
    client.business_name = business_name
    client.business_type = business_name
    client.transportation_method = transportation_method
    client.notes = notes
    client.save()
    print("####### Client created: " + client.first_name)

CreateClient('Zaldy', 'Conception', 'Male', 'zaldy@mailinator.com', '0927123456', True, '123 Market Avenue', 'Pasig', '12345', 'Philippines', 'San Miguel', 'Eloi & She Food Corner', 'Canteen', 'Tricycle', 'He is the man...or boyflux!')
CreateClient('Reyna', 'Banatao', 'Female', 'reyna@mailinator.com', '0927123456', True, '123 Birthing Avenue', 'Pasig', '12345', 'Philippines', 'Nagpayong', 'God Gift Lying In', 'Birthing Clinic', 'Tricycle', 'She has great ideas!')
CreateClient('Gerald', 'Taratao', 'Male', 'gerald@mailinator.com', '0927123456', True, '123 Petshop Avenue', 'Pasig', '12345', 'Philippines', 'Rosario', 'GAT Pet Shop', 'Petshop', 'Jeepney', 'Great guy!')

'''create assigned client'''
def CreateAssignedClient(intern_username, client_first_name):
    assigned_client = mod.AssignedClient()
    assigned_client.client = mod.Client.objects.get(first_name = client_first_name)
    assigned_client.intern = mod.Intern.objects.get(username = intern_username)
    assigned_client.save()
    print("####### assignment created: " + assigned_client.intern.first_name + ' has bookmarked ' + assigned_client.client.first_name)

CreateAssignedClient('jvclapier', 'Zaldy')
CreateAssignedClient('eaglauser', 'Zaldy')
CreateAssignedClient('bdsmith98', 'Gerald')
CreateAssignedClient('eaglauser', 'Reyna')
CreateAssignedClient('bdsmith98', 'Reyna')
CreateAssignedClient('jvclapier', 'Reyna')

'''create logs'''
def CreateLog(date_created, visit_description, next_steps, time_of_visit, intern_username, client_first_name):
    log = mod.Log()
    log.date_created = date_created
    log.visit_description = visit_description
    log.next_steps = next_steps
    log.time_of_visit = time_of_visit
    log.intern = mod.Intern.objects.get(username = intern_username)
    log.client = mod.Client.objects.get(first_name = client_first_name)
    log.save()
    print('####### New log for', log.client.first_name, 'created by', log.intern.first_name, 'on', log.date_created)

CreateLog('2018-06-25', 'Today we visited with Reyna about marekting materials and it was good stuff.', 'We are doing some things for her.', '10:00AM', 'jvclapier', 'Reyna')
CreateLog('2018-06-18', 'Today we visited with Gerald about an excel spreadsheet and he took us to lunch.', 'We are going to follow up and go to MOA.', '1:00PM', 'bdsmith98', 'Gerald')
CreateLog('2018-06-12', 'Zaldy has an awesome ponytail.', 'We are going to cut his ponytail.', '9:00AM', 'eaglauser', 'Zaldy')