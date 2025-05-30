from django.contrib import admin
from django.utils.html import format_html
from .models import Order,OrderProduct,Payment
import requests
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'get_payment_id', 'get_payment_method', 'cash_on_delivery','get_user_type',
        'full_name', 'email','order_total', 'status', 'created_at',
    )
    actions = ['send_to_courier']
    search_fields = ('order_number', 'user__first_name', 'user__last_name', 'email')
    list_filter = ('status', 'created_at', 'country')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ip')

    fields = (
        'user', 'payment', 'order_number', 
        'first_name', 'last_name', 'phone', 'email', 
        'address_line_1', 'address_line_2', 'country', 
        'state', 'city', 'order_note', 'order_total', 
        'tax','discount', 'shipping_fee', 'status'
    )
    def get_user_type(self, obj):
        if obj.user:  # Check if the user is registered
            return "Registered"
        if obj.email:  # Check if the email is available for guest orders
            return "Guest"
        return "Unknown"

    get_user_type.short_description = 'User Type'
    

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else "No User"
    full_name.short_description = 'Full Name'

    def get_payment_id(self, obj):
        return obj.payment.payment_id if obj.payment else "No Payment"
    get_payment_id.short_description = 'Payment ID'

    def get_payment_method(self, obj):
        return obj.payment.payment_method if obj.payment else "No Payment"
    get_payment_method.short_description = 'Payment Method'
    
    
    def send_to_courier(self, request, queryset):
        for order in queryset:
            response = self.place_order(order)  # Call the function to place order
            if response.status_code == 200:
                order.status = 'Sent'  # Update order status
                order.is_ordered = True
                order.save()  # Save the updated order
                self.message_user(request, f"Order {order.order_number} sent to courier successfully.")
            else:
                self.message_user(request, f"Failed to send order {order.order_number} to courier.", level='error')

    def place_order(self, order):
        api_key = 'f5be2olgolu0bfnodtuwk5suqbmgwthb'
        secret_key = 'w5coe2d5ymtddlayeudhaffm'
        base_url = 'https://portal.packzy.com/api/v1/create_order'
        headers = {
            "Api-Key": api_key,
            "Secret-Key": secret_key,
            "Content-Type": "application/json"
        }
        payload = {
            "invoice": order.order_number,
            "recipient_name": f"{order.first_name} {order.last_name}",
            "recipient_phone": order.phone,
            "recipient_address": f"{order.address_line_1}, {order.address_line_2}, {order.city}, {order.state}, {order.country}",
            "cod_amount": order.order_total if order.cash_on_delivery else 0,
            "note": order.order_note
        }
        response = requests.post(base_url, json=payload, headers=headers)
        return response

    send_to_courier.short_description = "Send selected orders to courier"
    
    

admin.site.register(Order, OrderAdmin)






class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 
        'customer_email', 
        'product_list',
        'color',
        'size', 
        'product_price', 
        'created_at', 
        'order_status',
        'user_type'  # New field to distinguish user types
    )

    def product_list(self, obj):
        products = OrderProduct.objects.filter(order=obj.order)
        product_details = [f"{prod.product.title} (×{prod.quantity})" for prod in products]
        return format_html('<br>'.join(product_details))
    product_list.short_description = 'Products'

    list_filter = ('ordered', 'created_at', 'product__category')  
    search_fields = (
        'product__title', 
        'user__email', 
        'order__email',  # Added search by order email
        'order__id'
    )  

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
        return super().get_queryset(request).select_related(
            'product', 'user', 'order'
        )

    def order_id(self, obj):
        return obj.order.id if obj.order else "N/A"
    order_id.short_description = 'Order ID'

    def customer_email(self, obj):
        # First try user email (registered users)
        if obj.user and obj.user.email:
            return obj.user.email
        # Fall back to order email (guest users)
        if obj.order and obj.order.email:
            return obj.order.email
        return "No email"
    customer_email.short_description = 'Customer Email'
    customer_email.admin_order_field = 'order__email'  # Enable sorting

    def order_status(self, obj):
        if obj.order:
            return obj.order.get_status_display()
        return "No status"
    order_status.short_description = 'Order Status'

    def user_type(self, obj):
        if obj.user:
            return "Registered"
        if obj.order and obj.order.email:
            return "Guest"
        return "Unknown"
    user_type.short_description = 'User Type'

admin.site.register(OrderProduct, OrderProductAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'amount_paid', 'status', )
    list_filter = ('status', )
    search_fields = ('payment_id', 'user__username', 'amount_paid')
admin.site.register(Payment,PaymentAdmin)