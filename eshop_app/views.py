from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View

from eshop_app.forms import CheckOutForm
from eshop_app.models import Item, OrderItem, Order, BillingAddress, Payment
from django.views.generic import ListView, DetailView
import stripe
from eshopper.secret_settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


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


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        context = {
            'form': form,
        }
        return render(self.request, 'eshop_app/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                address = form.cleaned_data.get('address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                # Todo: add payment options
                # same_shipping_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=self.request.user,
                    address=address,
                    apartment_address=apartment_address,
                    country=country,
                    zip_code=zip_code,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('shopapp:checkout')

            messages.info(self.request, 'Failed to checkout')
            return redirect('shopapp:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'you dont have an order')
            return redirect('shopapp:order_summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'eshop_app/payment.html')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, 'successfuly added')
            return redirect('/')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, 'Too many requests made to the API too quickly')
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, 'Invalid parameters were supplied to Stripes API')
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication with Stripe's API failed")
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, 'Network communication with Stripe failed')
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, 'Something is wrong')
            return redirect('/')

        except Exception as e:
            # send email to our selfs
            messages.error(self.request, 'This is serious error')
            return redirect('/')

        # Create payment


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
            if order_item.quantity > 1:
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
