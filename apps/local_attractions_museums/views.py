# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def hello_world(request):
    return HttpResponse(request.get_full_path())


def index(request):
    return render(request, "index.html")
