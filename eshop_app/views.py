from django.shortcuts import render


def index(request):
    return render(request, 'eshop_app/index.html', {})


def shop(request):
    return render(request, 'eshop_app/shop.html', {})


def err404(request):
    return render(request, 'eshop_app/404.html', {})
