from django.shortcuts import render,redirect,get_object_or_404 ,HttpResponse
import requests

from django.db.models import Avg  # Import Avg here
from .models import Product,Review,ProductColor,WishList
from .forms import ReviewForm
from django.contrib import messages
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from category .models import Category
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# Create your views here.


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def Index(request):
    products = Product.objects.all().order_by('-created_at')
    new_products = Product.objects.order_by('-created_at')[:52]
    
    return render(request,'shop/home2.html',{'products':products,'new_products':new_products})

def OureStore(request, category_slug=None):
    category = None
    products = None
    count = 0  # Initialize count

    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)  # Use correct field name
        paginator = Paginator(products,6) # Show 6 products in per page
        page = request.GET.get('page')
        pagged_products = paginator.get_page(page)
        count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products,6) # Show 6 products in per page
        page = request.GET.get('page')
        pagged_products = paginator.get_page(page)
        count = products.count()  # Count the number of available products
        
    return render(request, 'shop/store.html', {
        'products': pagged_products, 'count': count,
    })




def ProductDetail(request, category_slug, product_slug):
    # Initialize variables for savings and discount percentage
    savings = 0
    discount_percentage = 0
    # Get the product or return a 404 error if it doesn't exist
    products = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    # Handle recently viewed products
    recently_viewed_products = []
    if 'recently_viewed' in request.session:
        # Directly use the IDs from the session, assuming they are integers
        recently_viewed_ids = request.session['recently_viewed']
        recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids)
    
    # Add the current product to the recently viewed list
    if products.id not in request.session.get('recently_viewed', []):
        # Limit the number of recently viewed products (e.g., 5)
        recent_products = request.session.get('recently_viewed', [])
        recent_products.append(products.id)
        if len(recent_products) > 5:
            recent_products.pop(0)  # Remove the oldest viewed product
        request.session['recently_viewed'] = recent_products
        
        
    print('recently_viewed_products')


    # Now filter ProductColor based on the product instance
    product_color = ProductColor.objects.filter(product=products)
   
    # Get reviews for the product
    reviews = Review.objects.filter(product=products).order_by('-created_at')
    review_count = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = products
            review.save()
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('productDetails', category_slug=category_slug, product_slug=products.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()

    # Fetch related images
    images = products.additional_images.all()

    # Calculate savings and discount percentage
    if products.price is not None:
        savings = products.price - (products.discount_amount or 0)
        discount_percentage = (savings / products.price * 100) if products.price else 0

    # Increment views or last sale hours
    products.increment_last_sale_in_hours()

    # Sales message logic
    if products.last_sale_in_hours >= 24:
        days = products.last_sale_in_hours // 24
        hours = products.last_sale_in_hours % 24
        
        if hours > 0:
            sales_message = f"{products.items_sold} sold in the last {days} days and {hours} hours"
        else:
            sales_message = f"{products.items_sold} sold in the last {days} days"
    else:
        sales_message = f"{products.items_sold} sold in the last {products.last_sale_in_hours} hours"

    # Prepare context for rendering
    context = {
        'color': [pc.color_name for pc in product_color],
        'size': [pc.size for pc in product_color],
        'user_id': request.user.id if request.user.is_authenticated else None,
        'sales_message': sales_message,
        'items_sold': products.items_sold,
        'products': products,
        'savings': savings,
        'images': images,
        'form': form,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'discount_percentage': round(discount_percentage),
        'recently_viewed_products': (recently_viewed_products),
        
    }

    return render(request, 'shop/productDetail.html', context)


def WishListView(request):
    current_user = request.user
    if current_user.is_authenticated:
        wishlist_items = WishList.objects.filter(user=current_user)
        messages.info(request,f"{current_user.username} has {wishlist_items.count()} items in their wishList")
    else:
        wishlist_items = []
    context={
        'wishlist_items':wishlist_items
    }
   
    return render(request, 'shop/wishlist.html',context)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Check if the product is already in the user's wishlist
    wishlist_item, created = WishList.objects.get_or_create(user=request.user, wish_product=product)

    if created:
        messages.success(request, f"{product.title} has been added to your wishlist.")
    else:
        messages.info(request, f"{product.title} is already in your wishlist.")

    return redirect('myWishList')  # Redirect to the wishlist page

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishList, id=item_id)
    item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('myWishList')


def LoadProducts(request):
     r  = requests.get('https://fakestoreapi.com/products')
     
     print(r.json())
     for item in r.json():
        
         product = Product(
             title = item['title'],
             description = item['description'],
             price = item['price'],
             images = item['image'],
             ratings=item['rating']['rate'],  # Average rating
             is_available=item['rating']['count'],  # Number of ratings    
         )
         product.save()
         
         return HttpResponse()
         
   
     