from django.shortcuts import render,redirect,get_object_or_404 ,HttpResponse
import requests
from datetime import datetime,timedelta
from django.utils import timezone
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
from django.utils.text import slugify
# Create your views here.


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def Index(request):
    products = Product.objects.all().order_by('-created_at')
     # Check the quantity_left for each product
    for product in products:
        print(f"Product: {product.title}, Quantity Left: {product.quantity_left}")
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
    current_time = timezone.now()
    # Initialize variables for savings and discount percentage
    savings = 0
    discount_percentage = 0
    # Get the product or return a 404 error if it doesn't exist
    products = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    # Calculate how long ago items were sold
      # Calculate how long ago items were sold
    sold_time = products.last_sold_time  # Replace with the actual field for sold time
     # Fetch related products for the current product instance
    related_products = products.related_products.all()  # Access related products from the specific instance
    print(f"Related products count for {products.title}: {related_products.count()}")

    # Ensure sold_time is timezone-aware
    if sold_time and sold_time.tzinfo is None:
        sold_time = timezone.make_aware(sold_time)

    time_difference = current_time - sold_time if sold_time else None
    if time_difference:
        if time_difference < timedelta(hours=1):
            time_message = f"in the last {int(time_difference.total_seconds() // 60)} minutes"
        elif time_difference < timedelta(days=1):
            time_message = f"in the last {int(time_difference.total_seconds() // 3600)} hours"
        elif time_difference < timedelta(days=2):
            time_message = "yesterday"
        else:
            time_message = "more than one day ago"
    else:
        time_message = "not sold yet"
    
    
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
    # Prepare context for rendering
    context = {
        'current_time':current_time,
        'time_message':time_message,
        'color': [pc.color_name for pc in product_color],
        'size': [pc.size for pc in product_color],
        'user_id': request.user.id if request.user.is_authenticated else None,
        'items_sold': products.items_sold,
        'quantity_left': products.quantity_left,
        'products': products,
        'savings': savings,
        'images': images,
        'form': form,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'discount_percentage': round(discount_percentage),
        'recently_viewed_products': (recently_viewed_products),
        'related_products': related_products,
        
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
    try:
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}")

    products_data = response.json()

    for item in products_data:
        # Get or create the category
        category, created = Category.objects.get_or_create(name=item['category'])

        # Create a new product instance
        product = Product(
            title=item['title'],
            slug=slugify(item['title']),  # Generate slug from title
            description=item['description'],
            price=item['price'],
            ratings_count=item['rating']['count'],
            sku=f'sku-{item["id"]}',  # Generate a unique SKU
            category=category,
            stock=1,  # Set stock as appropriate (update logic as needed)
            is_available=item['rating']['count'] > 0,  # Example logic for availability
            images=item['image'],  # Handle this appropriately if saving to ImageField
            # Add other fields as needed, defaults or null if applicable
        )

        try:
            product.save()  # Save the product instance
        except Exception as e:
            print(f"Failed to save product {item['title']}: {e}")

    return HttpResponse("Products loaded successfully.")
   
     