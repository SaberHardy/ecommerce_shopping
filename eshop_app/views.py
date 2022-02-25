from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from eshop_app.models import Item, OrderItem, Order
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


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
                    item=item,
                    user=request.user,
                    ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        print(f'check the order item in the order = {order}')
        print(f'order_qs = {order_qs}')
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return redirect('shopapp:product', slug=slug)
        else:
            order.items.add(order_item)
            redirect('shopapp:product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect('shopapp:product', slug=slug)
