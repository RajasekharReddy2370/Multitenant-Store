from .models import Vendor
from django.utils.deprecation import MiddlewareMixin

class TenantMiddleware(MiddlewareMixin):
    """
    Resolve tenant from request header X-Tenant-Domain or subdomain.
    Sets request.tenant to the Vendor instance or None.
    """
    def process_request(self, request):
        domain = request.META.get("HTTP_X_TENANT_DOMAIN") or request.get_host().split(":")[0]
        # If domain is the main host (no tenant), you may want to skip or set None
        try:
            vendor = Vendor.objects.get(domain=domain)
        except Vendor.DoesNotExist:
            vendor = None
        request.tenant = vendor
