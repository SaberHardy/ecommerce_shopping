from django.urls import path
from . import views

app_name = 'shopapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('detail/<str:slug>/', views.ItemDetailView.as_view(), name='product'),
    path('error404/', views.error404, name='err404'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog_view, name='blog'),
    path('blog_detail/', views.detail_blog_view, name='detail_blog_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_to_cart/<str:slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<str:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('order_summary/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('remove_single_item_from_cart/<slug>/', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),
]
