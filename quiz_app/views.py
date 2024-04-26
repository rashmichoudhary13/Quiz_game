from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from .coding import webcam # Importing the webcam function from coding.py
from .gk import webcam_gk

# Create your views here.
def index(request):
    return render(request, 'index.html')

def coding(request):
    return webcam(request)

def gk(request):
    return webcam_gk(request)
    