from django.contrib import admin
from .models import Vendor, Product, Order, OrderItem, User, Customer
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Tenant / Role", {"fields": ("role","vendor")}),
    )

admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Customer)
