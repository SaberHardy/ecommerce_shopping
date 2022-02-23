from django.shortcuts import render

from eshop_app.models import Item


def index(request):
    return render(request, 'eshop_app/index.html', {})


def item_list(request):
    items = Item.objects.all()
    context = {
        'items': items
    }
    return render(request, 'eshop_app/item_list.html', context=context)


def err404(request):
    return render(request, 'eshop_app/404.html', {})
