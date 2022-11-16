from django.http import HttpRequest
from django.shortcuts import render


def zapier(request: HttpRequest):
    return render(request, "zapier.html")
