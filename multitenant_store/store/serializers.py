from rest_framework import serializers
from .models import Product, Order, OrderItem, User, Vendor, Customer
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["id", "name", "contact_email", "domain"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "username", "email", "role", "vendor", "first_name", "last_name"]
        read_only_fields = ["vendor"]  # vendor set at registration or by owner

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    vendor_domain = serializers.CharField(write_only=True, required=False, help_text="Vendor domain to register under (owners)")

    class Meta:
        model = UserModel
        fields = ["id","username","email","password","role","vendor_domain","first_name","last_name"]

    def create(self, validated_data):
        vendor_domain = validated_data.pop("vendor_domain", None)
        role = validated_data.get("role")
        if role == UserModel.ROLE_OWNER:
            # create vendor if domain provided
            if not vendor_domain:
                raise serializers.ValidationError({"vendor_domain": "required for owner registration"})
            vendor, _ = Vendor.objects.get_or_create(domain=vendor_domain, defaults={"name": f"{validated_data.get('username')}'s store", "contact_email": validated_data.get("email")})
            validated_data["vendor"] = vendor
        else:
            # For staff/customers we expect header-based tenant or set vendor in context
            vendor = self.context["request"].tenant
            if not vendor:
                raise serializers.ValidationError("No tenant available. Provide X-Tenant-Domain header.")
            validated_data["vendor"] = vendor

        password = validated_data.pop("password")
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        if user.role == UserModel.ROLE_CUSTOMER:
            Customer.objects.create(user=user, vendor=vendor)
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","name","description","price","stock","vendor","created_at"]
        read_only_fields = ["vendor","created_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]
        extra_kwargs = {
            "price": {"read_only": True}
        }

    def create(self, validated_data):
        product = validated_data["product"]
        validated_data["price"] = product.price
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ["id","vendor","customer","created_at","status","total","items","assigned_to"]
        read_only_fields = ["vendor","created_at","total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        vendor = self.context["request"].tenant
        request = self.context["request"]
        if not vendor:
            raise serializers.ValidationError("No tenant set")

        # link customer if authenticated and is customer
        if request.user.is_authenticated and request.user.role == request.user.ROLE_CUSTOMER:
            customer = getattr(request.user, "customer_profile", None)
        else:
            customer = None

        order = Order.objects.create(vendor=vendor, customer=customer, **validated_data)
        total = 0
        for item in items_data:
            product = item["product"]
            if product.vendor != vendor:
                raise serializers.ValidationError("Product does not belong to tenant")
            qty = item["quantity"]
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
            total += price * qty
            # optionally decrement stock
            product.stock = max(0, product.stock - qty)
            product.save()
        order.total = total
        order.save()
        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class AssignStaffSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['staff_id']

    def validate_staff_id(self, value):
        if not User.objects.filter(id=value, role='staff').exists():
            raise serializers.ValidationError("Staff member does not exist.")
        return value

    def update(self, instance, validated_data):
        staff_id = validated_data.get('staff_id')
        instance.assigned_staff_id = staff_id
        instance.save()
        return instance