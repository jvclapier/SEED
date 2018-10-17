"""seedsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from homepage import users, index, authentication
from homepage import addLog, clients, search

urlpatterns = [
    path('index/', index.index, name='index'),
    path('', authentication.login, name='login'),
    path('login/', authentication.login, name='login'),
    path('logout/', authentication.logout, name='logout'),
    path('add_log/<int:id>', addLog.add_log, name='add_log'),
    path('add_client/', clients.add_client, name='add_client'),
    path('client_profile/<int:id>', clients.client_profile, name='client_profile'),
    path('edit_client/<int:id>', clients.edit_client, name='edit_client'),
    path('delete_client/<int:id>', clients.delete_client, name='delete_client'),
    path('inactive_clients/', clients.inactive_clients, name='inactive_clients'),
    path('search/', search.search, name='search'),
    path('search_interns/', search.search_interns, name='search_interns'),
    path('add_bookmark/<int:id>', users.add_bookmark, name='add_bookmark'),
    path('admin_portal/', users.admin_portal, name='admin_portal'),
    path('intern_portal/', users.intern_portal, name='intern_portal'),
    path('edit_profile/', users.edit_profile, name='edit_profile'),
    path('admin_edit_profile/<int:id>', users.admin_edit_profile, name='admin_edit_profile'),
    path('add_intern/', users.add_intern, name='add_intern'),
    path('deactivate_intern/<int:id>', users.deactivate_intern, name='deactivate_intern'),
]
