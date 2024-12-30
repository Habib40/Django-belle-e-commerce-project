from django.contrib import admin
from .models import Order,OrderProduct,Payment
# Register your models here.

admin.site.register(Order)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'product', 'color', 'size', 'quantity', 'product_price', 'created_at', 'ordered')
    list_filter = ('ordered', 'created_at')
    search_fields = ('product__title', 'user__email')
    
    # Specify the fields you want to be read-only
    readonly_fields = ('order', 'payment', 'user', 'product', 'color', 'size', 'quantity', 'product_price', 'ordered', 'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Selecting related fields (only foreign keys)
        return qs.select_related('product', 'user', 'order')

admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Payment)