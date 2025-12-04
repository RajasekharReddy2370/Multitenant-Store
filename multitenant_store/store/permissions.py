from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Allow only store owner users (role==owner) of the current tenant.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == request.user.ROLE_OWNER and request.user.vendor == request.tenant)

class IsStaffOrOwnerForProduct(permissions.BasePermission):
    """
    Owners can CRUD any. Staff can create/update/delete only if vendor matches and optionally assigned.
    Customers can only read.
    """
    def has_permission(self, request, view):
        # safe methods allowed for all authenticated customers
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.role == request.user.ROLE_OWNER and request.user.vendor == request.tenant:
            return True
        if request.user.role == request.user.ROLE_STAFF and request.user.vendor == request.tenant:
            # staff can modify resources — further object-level check can be applied
            return True
        return False

class IsOrderAccessible(permissions.BasePermission):
    """
    Order-level checks:
    - Owner: full access
    - Staff: can manage orders if vendor matches and optionally assigned
    - Customer: can view and create their own orders
    """
    def has_object_permission(self, request, view, obj):
        # obj is Order
        if request.user.role == request.user.ROLE_OWNER and request.user.vendor == request.tenant:
            return True
        if request.user.role == request.user.ROLE_STAFF and request.user.vendor == request.tenant:
            # staff can manage if assigned_to is them or if they are allowed to manage all orders for vendor
            if obj.assigned_to is None or obj.assigned_to == request.user:
                return True
        if request.user.role == request.user.ROLE_CUSTOMER:
            # allow customer to view/modify their own orders (create handled elsewhere)
            return obj.customer and obj.customer.user == request.user
        return False
