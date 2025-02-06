from django.contrib import admin
from django.utils.html import format_html
from .models import Order,OrderProduct,Payment
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'get_payment_id', 'get_payment_method', 'cash_on_delivery',
        'full_name', 'email', 'order_total', 'status', 'created_at',
    )
    search_fields = ('order_number', 'user__first_name', 'user__last_name', 'email')
    list_filter = ('status', 'created_at', 'country')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ip')

    fields = (
        'user', 'payment', 'order_number', 
        'first_name', 'last_name', 'phone', 'email', 
        'address_line_1', 'address_line_2', 'country', 
        'state', 'city', 'order_note', 'order_total', 
        'tax', 'shipping_fee', 'status'
    )

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else "No User"
    full_name.short_description = 'Full Name'

    def get_payment_id(self, obj):
        return obj.payment.payment_id if obj.payment else "No Payment"
    get_payment_id.short_description = 'Payment ID'

    def get_payment_method(self, obj):
        return obj.payment.payment_method if obj.payment else "No Payment"
    get_payment_method.short_description = 'Payment Method'

admin.site.register(Order, OrderAdmin)


class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 
        'customer_email', 
        'product_list',  # This will show grouped products
        'discount',
        'color' ,
        'size', 
        'product_price', 
        'created_at', 
        'order_status'
    )

    def product_list(self, obj):
        products = obj.order.orderproduct_set.all()  # Assuming this relationship exists
        product_details = [f"- {prod.product.title}" for prod in products]
        return format_html('<br>'.join(product_details))  # Use format_html to render HTML safely
    product_list.short_description = 'Products'

    list_filter = ('ordered', 'created_at', 'product__category')  
    search_fields = ('product__title', 'user__email', 'order__id')  

    readonly_fields = (
        'order', 
        'payment', 
        'user', 
        'product', 
        'color', 
        'size',  
        'product_price', 
        'ordered', 
        'created_at', 
        'updated_at'
    )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product', 'user', 'order')

    def order_id(self, obj):
        return obj.order.id  
    order_id.short_description = 'Order ID'

    def customer_email(self, obj):
        return obj.user.email  
    customer_email.short_description = 'Customer Email'

    def order_status(self, obj):
        return "Completed" if obj.ordered else "Pending"
    order_status.short_description = 'Order Status'

admin.site.register(OrderProduct, OrderProductAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'amount_paid', 'status', )
    list_filter = ('status', )
    search_fields = ('payment_id', 'user__username', 'amount_paid')
admin.site.register(Payment,PaymentAdmin)