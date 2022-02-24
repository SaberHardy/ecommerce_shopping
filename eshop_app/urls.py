from django.urls import path
from . import views

app_name = 'shopapp'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('detail/<str:slug>/', views.ItemDetailView.as_view(), name='detail'),
    path('error404/', views.error404, name='err404'),
    path('checkout/', views.checkout, name='checkout'),
]
