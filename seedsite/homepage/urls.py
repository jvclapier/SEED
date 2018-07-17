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
from homepage import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.login, name='login'),
    path('add_log/<int:id>', views.add_log, name='add_log'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('client_profile/<int:id>', views.client_profile, name='client_profile'),
    path('edit_client/<int:id>', views.edit_client, name='edit_client'),
    path('add_client/', views.add_client, name='add_client'),
    path('search/', views.search, name='search'),
    path('add_bookmark/<int:id>', views.add_bookmark, name='add_bookmark'),
    path('admin_portal/', views.admin_portal, name='admin_portal'),
    path('intern_portal/', views.intern_portal, name='intern_portal'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_intern/', views.add_intern, name='add_intern'),
    path('delete_client/<int:id>', views.delete_client, name='delete_client'),
    path('search_interns/', views.search_interns, name='search_interns')

]
