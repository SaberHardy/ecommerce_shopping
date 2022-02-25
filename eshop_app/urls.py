from django.urls import path
from . import views

app_name = 'shopapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('detail/<str:slug>/', views.ItemDetailView.as_view(), name='product'),
    path('error404/', views.error404, name='err404'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_to_cart/<str:slug>/', views.add_to_cart, name='add_to_cart'),
]
