from django.urls import path
from . import views

app_name = 'shopapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.item_list, name='index'),
    path('404/', views.err404, name='err404'),
]
