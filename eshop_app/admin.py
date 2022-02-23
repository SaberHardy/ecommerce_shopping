from django.contrib import admin

from eshop_app.models import *

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
