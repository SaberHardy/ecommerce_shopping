from django.shortcuts import render


def index(request):
    return render(request, 'eshop_app/index.html', {})