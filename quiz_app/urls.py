from django.contrib import admin
from django.urls import path
from quiz_app import views

urlpatterns = [
    path("",views.index, name="home"),
    path('webcam/', views.webcam, name='webcam'),
]