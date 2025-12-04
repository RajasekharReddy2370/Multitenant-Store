from django.db import models
from django.contrib.auth.models import AbstractUser

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    domain = models.CharField(max_length=255, unique=True, help_text="domain or subdomain for tenant")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_OWNER = "owner"
    ROLE_STAFF = "staff"
    ROLE_CUSTOMER = "customer"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_STAFF, "Staff"),
        (ROLE_CUSTOMER, "Customer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE, related_name="users")
    # staff may have assignment to orders (optional); keep FK on Order.or_assigned_to

    def __str__(self):
        return f"{self.username} ({self.role})"

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.vendor.name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Customer {self.user.username} ({self.vendor.name})"

class Order(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assigned_to = models.ForeignKey("User", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_orders")

    def __str__(self):
        return f"Order {self.id} - {self.vendor.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
