from django.shortcuts import render,redirect,get_object_or_404
from.forms import RegistrationForm,LoginForm
from django.contrib.auth import authenticate,login
from .models import Account
from django.contrib import messages,auth
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from cart. models import Cart,CartItem
from cart. views import _cart_id
from shop. views import Product
from order.models import OrderProduct,Order # Import your OrderProduct model
# for email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
import requests
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class RegisterView(View):
    def get(self, request):
        forms = RegistrationForm()
        return render(request, 'accounts/register.html', {'forms': forms})

    def post(self, request):
        forms = RegistrationForm(request.POST)
        if forms.is_valid():
            first_name = forms.cleaned_data['first_name']
            last_name = forms.cleaned_data['last_name']
            phone_number = forms.cleaned_data['phone_number']
            email = forms.cleaned_data['email']
            password = forms.cleaned_data['password']
            
            # Create the user using the custom manager
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email.split('@')[0],  # Assuming email before @ as username
                email=email,
                password=password,
                phone_number=phone_number
                
            )
            user.phone_number = phone_number
            
           
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            mail_body = render_to_string('accounts/account_activate_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)             
            })
            to_email = email
            from_email = 'habibkb5080@gmail.com'  # Replace with your sender email
            send_mail(mail_subject, mail_body, from_email, [to_email], fail_silently=False)

            return redirect("/accounts/login/?commands=verification&email=" +email)
        else:
            # If the form is not valid, show error messages
            for error in forms.errors.values():
                messages.error(request, error)

        return render(request, 'accounts/register.html', {'forms': forms})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                # Get or create the user's cart
                cart, created = Cart.objects.get_or_create(user=user)
                session_cart_items = request.session.get('cart_items', [])

                # Handle session cart items
                for session_item in session_cart_items:
                    product = get_object_or_404(Product, id=session_item['product_id'])
                    color = session_item['color']
                    size = session_item['size']
                    quantity = session_item['quantity']

                    # Create or update the CartItem for the user
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        color=color,
                        size=size,
                        defaults={'quantity': quantity, 'user': user}  # Assign user here
                    )

                    if not created:
                        # Update the existing item with the new quantity and user if needed
                        cart_item.quantity += quantity
                        cart_item.user = user  # Ensure user is set
                        cart_item.save()

                # Clear the session cart items after transferring to the user's cart
                del request.session['cart_items']

            except Exception as e:  # Catch any exception
                # messages.error(request, 'An error occurred while accessing the cart.')  # General error message
                pass

            auth.login(request, user)
            messages.success(request, 'You are logged in!')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                next_page = params.get('next', 'dashboard')  # Default to dashboard if no next page
                return redirect(next_page)
            except Exception as e:
                return redirect('dashboard')  # Redirect to a success page after login

        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def Logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out!")
    return redirect('login')
   
   
   
def Activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        
        





@login_required(login_url='login')
def Dashboard(request):
    try:
        # Fetch Order instances for the logged-in user, ordered by creation date
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        # Initialize a list to hold the Order and OrderProduct instances
        order_details = []
        for order in orders:
            # Get related OrderProduct records
            order_products = OrderProduct.objects.filter(order=order).select_related('product')
            # Append the order and its products directly to the list
            order_details.append({
                'order': order,
                'order_products': order_products
            })
        
        # Render the dashboard template with the order details
        return render(request, 'accounts/dashboard.html', {
            'order_details': order_details,
            'messages': request.session.pop('messages', [])  # Optional: to pass messages if any
        })
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
    
    
    
    
    
    
    
    
    
    
    

class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email.split('@')[0],
                email=email,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            mail_body = render_to_string('accounts/account_activate_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            from_email = 'habibkb5080@gmail.com'
            send_mail(mail_subject, mail_body, from_email, [to_email], fail_silently=False)

            return redirect("/accounts/login/?commands=verification&email=" + email)
        else:
            for error in form.errors.values():
                messages.error(request, error)

        return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart, created = Cart.objects.get_or_create(user=user)
                session_cart_items = request.session.get('cart_items', [])

                for session_item in session_cart_items:
                    product = get_object_or_404(Product, id=session_item['product_id'])
                    color = session_item['color']
                    size = session_item['size']
                    quantity = session_item['quantity']

                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        color=color,
                        size=size,
                        defaults={'quantity': quantity, 'user': user}
                    )

                    if not created:
                        cart_item.quantity += quantity
                        cart_item.user = user
                        cart_item.save()

                del request.session['cart_items']

            except Exception as e:
                pass

            auth.login(request, user)
            messages.success(request, 'You are logged in!')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                next_page = params.get('next', 'dashboard')
                return redirect(next_page)
            except Exception as e:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def Logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out!")
    return redirect('login')

def Activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')

@login_required(login_url='login')
def Dashboard(request):
    print("Problem in dashboard")
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        order_details = []

        for order in orders:
            order_products = OrderProduct.objects.filter(order=order).select_related('product')
            subtotal = 0  # Use float instead of Decimal

            for order_product in order_products:
                # Ensure discount_amount is a valid float
                try:
                    discount_amount = float(order_product.discount_amount)
                except (ValueError, TypeError) as e:
                    print(f"Invalid discount amount: {order_product.discount_amount}, Error: {e}")
                    discount_amount = 0 # Default to 0

                # Ensure quantity is a valid float
                try:
                    quantity_value = str(order_product.quantity) # Convert to string and strip whitespace
                    quantity = float(quantity_value)
                except (ValueError, TypeError) as e:
                    print(f"Invalid quantity: {order_product.quantity}, Error: {e}")
                    quantity = 0  # Default to 0

                print(f"Calculating subtotal... Discount Amount: {discount_amount}, Quantity: {quantity}")

                subtotal += discount_amount * quantity

            # Calculate shipping fee
            shipping_fee = float(order.shipping_fee) if order.shipping_fee else 0.00
            tax = subtotal * 0.02
            total = subtotal + shipping_fee + tax

            order_details.append({
                'order': order,
                'order_products': order_products,
                'subtotal': subtotal,
                'shipping_fee': shipping_fee,
                'tax': tax,
                'total': total,
            })

        context = {
            'order_details': order_details,
        }
        return render(request, 'accounts/dashboard.html', context)

    except Exception as e:
        print(f"Error retrieving orders or order products: {e}")
        return render(request, 'accounts/dashboard.html', {'error': 'Could not retrieve orders or order products.'})
    
    
def FogotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Password To Access Your Account'
            mail_body = render_to_string('accounts/forgot_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            from_email = 'habibkb5080@gmail.com'
            send_mail(mail_subject, mail_body, from_email, [to_email], fail_silently=False)
            messages.success(request, 'To reset your password, please check your email.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist with this email.')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')

def ResetPasswordValidation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect(reverse('resetPassword'))
    else:
        messages.error(request, 'Invalid token.')
        return redirect(reverse('forgotPassword'))


    
def FogotPassword(request):
    if request.method=='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user =Account.objects.get(email__exact=email)
          
            current_site = get_current_site(request)
            mail_subject = 'Reset Password To Access Your Account'
            mail_body = render_to_string('accounts/forgot_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)             
            })
            to_email = email
            from_email = 'habibkb5080@gmail.com'  # Replace with your sender email
            send_mail(mail_subject, mail_body, from_email, [to_email], fail_silently=False)
            messages.success(request,'To reset your password, please check your email.')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist with this email.')
            return redirect('forgotPassword') 
    return render(request, 'accounts/forgotPsaaword.html')




def ResetPasswordValidation(request, uidb64, token):
    try:
        # Decode the uidb64 and convert to a string or integer
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid  # Store the uid in the session
        messages.success(request, 'Please reset your password.')
        return redirect(reverse('resetPassword'))
    else:
        messages.error(request, 'Invalid token.')
        return redirect(reverse('forgotPassword'))
            
def ResetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password and confirm_password:  # Check if both values are present
            if password == confirm_password:
                uid = request.session.get('uid')
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request,'Password reset successfull.Now you can login')
                return redirect('login')
            else:
                messages.error(request, 'Password does not match!')
                return redirect('resetPassword')  
    else:          
      return render(request, 'accounts/resetPassword.html')