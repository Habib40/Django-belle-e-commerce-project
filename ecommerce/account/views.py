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
                password=password
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
    
    
    



# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = auth.authenticate(request, email=email, password=password)

#         if user is not None:
#             try:
#                 # Ensure the session cart ID exists
#                 cart_id = request.session.get('cart_id', None)  # Retrieve cart ID from session
#                 logger.debug(f'Cart ID retrieved: {cart_id}')  # Debug log

#                 if cart_id:
#                     # Retrieve or create the user's cart
#                     user_cart, created = Cart.objects.get_or_create(user=user)
#                     logger.debug(f'User cart retrieved/created: {user_cart.cart_id}')  # Debug log

#                     # Retrieve session cart items
#                     session_cart_items = CartItem.objects.filter(cart__cart_id=cart_id)

#                     # Create a dictionary of user's current cart items for easy access
#                     user_cart_items = CartItem.objects.filter(cart=user_cart)
#                     user_cart_dict = {(item.product.id, item.color, item.size): item for item in user_cart_items}

#                     # Transfer session cart items to the user's cart
#                     for session_item in session_cart_items:
#                         key = (session_item.product.id, session_item.color, session_item.size)

#                         if key in user_cart_dict:
#                             # If item already exists in user's cart, update quantity
#                             existing_item = user_cart_dict[key]
#                             existing_item.quantity += session_item.quantity
#                             existing_item.save()
#                             logger.debug(f'Updated existing item: {existing_item}')  # Debug log
#                         else:
#                             # Add new item to user's cart
#                             session_item.cart = user_cart
#                             session_item.user = user
#                             session_item.save()
#                             logger.debug(f'Added new item to user cart: {session_item}')  # Debug log

                   

#                 else:
#                     logger.debug('No cart ID found in session.')  # Debug log

#             except Exception as e:
#                 messages.error(request, f'An error occurred: {str(e)}')
#                 logger.error(f'Error during cart transfer: {str(e)}')  # Log the error

#             # Log the user in
#             auth.login(request, user)
#             messages.success(request, 'You are logged in!')
#             return redirect(request.GET.get('next', 'dashboard'))  # Redirect to the next page or dashboard
#         else:
#             messages.error(request, 'Invalid login credentials.')
#             return redirect('login')

#     return render(request, 'accounts/login.html')

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
    # Attempt to retrieve the user's cart
    try:
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Log for debugging
        if created:
            print(f"Created new cart for user: {request.user.id}")
        else:
            print(f"Using existing cart for user: {request.user.id}")

        # Retrieve cart items for display
        cart_items = CartItem.objects.filter(cart=cart)
        
        # Render the dashboard with the cart and its items
        return render(request, 'accounts/dashboard.html', {'cart': cart, 'cart_items': cart_items})

    except Exception as e:
        print(f"Error retrieving cart: {e}")
        return render(request, 'accounts/dashboard.html', {'error': 'Could not retrieve cart.'})


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