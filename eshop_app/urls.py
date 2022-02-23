from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='index'),
    path('404/', views.err404, name='err404'),
]
