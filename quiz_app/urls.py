from django.contrib import admin
from django.urls import path
from quiz_app import views

urlpatterns = [
    path("",views.index, name="home"),
    path('coding/', views.coding, name='coding'),
    path('gk/', views.gk, name='gk'),
]