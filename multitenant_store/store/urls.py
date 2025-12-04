from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, RegisterView, VendorViewSet
from .jwt import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OrderStatusUpdateView, AssignStaffToOrderView, MyOrdersView



router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"vendors", VendorViewSet, basename="vendor")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<int:pk>/assign-staff/', AssignStaffToOrderView.as_view(), name='assign-staff'),
    path('orders/my/', MyOrdersView.as_view(), name='my-orders'),
    path("", include(router.urls)),
]
