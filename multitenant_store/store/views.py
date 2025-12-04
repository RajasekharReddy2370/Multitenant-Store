from rest_framework import viewsets, status, generics, permissions
from .models import Product, Order, Vendor, User, Customer
from .serializers import ProductSerializer, OrderSerializer, RegisterSerializer, UserSerializer, VendorSerializer
from .permissions import IsStaffOrOwnerForProduct, IsOrderAccessible, IsOwner
from rest_framework.response import Response
from .jwt import MyTokenObtainPairView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import OrderStatusSerializer, AssignStaffSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsOwner]  # only owner can create/update vendor (domain registration flow might differ)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrOwnerForProduct]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Product.objects.none()
        return Product.objects.filter(vendor=tenant)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.tenant)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    # default permission: authenticated; object-level checks below
    permission_classes = [permissions.IsAuthenticated, IsOrderAccessible]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant is None:
            return Order.objects.none()
        qs = Order.objects.filter(vendor=tenant).order_by("-created_at")
        user = self.request.user
        if user.is_authenticated and user.role == user.ROLE_CUSTOMER:
            # customers see their orders only
            try:
                cust = user.customer_profile
                qs = qs.filter(customer=cust)
            except Customer.DoesNotExist:
                qs = Order.objects.none()
        return qs

    def perform_create(self, serializer):
        serializer.save()

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    http_method_names = ['patch']

class AssignStaffToOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AssignStaffSerializer
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        staff_id = serializer.validated_data.get("staff_id")
        staff = User.objects.get(id=staff_id)

        return Response(
            {
                "order_id": instance.id,
                "staff_id": staff_id,
                "staff_name": staff.username,
                "vendor": instance.vendor.name if instance.vendor else None,
                "status": "Staff assigned successfully"
            },
            status=status.HTTP_200_OK
        )


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        vendor = self.request.tenant  # from middleware
        
        # Get the customer linked to this user + vendor
        customer = Customer.objects.get(user=user, vendor=vendor)
        
        return Order.objects.filter(customer=customer, vendor=vendor)