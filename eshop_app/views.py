from django.shortcuts import render
from eshop_app.models import Item
from django.views.generic import ListView, DetailView


class HomeView(ListView):
    model = Item
    template_name = 'eshop_app/home.html'


def products(request):
    items = Item.objects.all()
    context = {
        'items': items
    }
    return render(request, 'eshop_app/home.html', context)


def checkout(request):
    return render(request, 'eshop_app/checkout.html', {})


def error404(request):
    return render(request, 'eshop_app/404.html', {})


class ItemDetailView(DetailView):
    model = Item
    template_name = 'eshop_app/product-details.html'
