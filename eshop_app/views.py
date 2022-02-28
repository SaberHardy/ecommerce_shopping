from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View

from eshop_app.models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView


class HomeView(ListView):
    model = Item
    paginate_by = 2
    template_name = 'eshop_app/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        last_3_items = Item.objects.order_by('-title')[:3]

        context.update({
            'last_3_items': last_3_items,
        })
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    # model = Order
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'eshop_app/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'you dont have an order')
            return redirect('/')
    # template_name = 'eshop_app/cart.html'


def products(request):
    items = Item.objects.all()
    last_3_items = Item.objects.all()
    print(f"last item is: {last_3_items}")
    context = {
        'items': items,
        'last_3_items': last_3_items,
    }
    return render(request, 'eshop_app/home.html', context)


def checkout(request):
    return render(request, 'eshop_app/checkout.html', {})


def error404(request):
    return render(request, 'eshop_app/404.html', {})


class ItemDetailView(DetailView):
    model = Item
    template_name = 'eshop_app/product-details.html'

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        recommended_items = Item.objects.order_by('-title')[:3]
        context.update({
            'recommended_items': recommended_items
        })
        return context


@login_required
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

            messages.info(request, 'This item quantity was updated!')
            return redirect('shopapp:order_summary')
        else:
            order.items.add(order_item)

            messages.info(request, 'This item was added to your cart!')
            return redirect('shopapp:order_summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)

        messages.info(request, 'This item was added to your cart')
        return redirect('shopapp:order_summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # Check if there is any order for user
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)

            messages.info(request, 'This item was removed from your cart')
            return redirect('shopapp:order_summary')
        else:
            messages.info(request, 'This item was not in your cart')
            return redirect('shopapp:product', slug=slug)

    else:
        messages.info(request, 'You do not have an active order')
        return redirect('shopapp:product', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        # Check if there is any order for user
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, 'This item quantity was updated')
            return redirect('shopapp:order_summary')
        else:
            messages.info(request, 'This item was not in your cart')
            return redirect('shopapp:product', slug=slug)

    else:
        messages.info(request, 'You do not have an active order')
        return redirect('shopapp:product', slug=slug)


def contact(request):
    return render(request, 'eshop_app/contact-us.html')


def blog_view(request):
    return render(request, 'eshop_app/blog.html')


def detail_blog_view(request):
    return render(request, 'eshop_app/blog-single.html')
