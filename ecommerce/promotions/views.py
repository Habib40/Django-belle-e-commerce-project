from django.shortcuts import render
from cart.models import Cart
from .models import Coupon
from django.contrib import messages
from django.shortcuts import redirect,get_object_or_404
# Create your views here.

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            if coupon.is_valid():
                cart = Cart.objects.get(user=request.user)
                cart.coupon = coupon
                cart.save()
                messages.success(request, "Coupon applied successfully!")
            else:
                messages.error(request, "Coupon is not valid.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
    return redirect('carts')