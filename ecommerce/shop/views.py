from django.shortcuts import render,redirect,get_object_or_404 ,HttpResponse
import requests

from django.db.models import Avg  # Import Avg here
from .models import Product,Review,ProductColor
from .forms import ReviewForm
from django.contrib import messages
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def Index(request):
    products = Product.objects.all().order_by('-created_at')
    new_products = Product.objects.order_by('-created_at')[:52]
    
    return render(request,'shop/home2.html',{'products':products,'new_products':new_products})


def ProductDetail(request, product_id, product_slug):
    # Initialize variables for savings and discount percentage
    savings = 0
    discount_percentage = 0

    # Get the product or return a 404 error if it doesn't exist
    products = get_object_or_404(Product, id=product_id, slug=product_slug)
    product_color = ProductColor.objects.filter(product_id=product_id)
   
    # Get reviews for the product
    reviews = Review.objects.filter(product=products).order_by('-created_at')
    review_count = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Handle review submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)  # Create a review instance but don't save it yet
            review.product = products  # Associate the review with the product
            review.save()  # Save the review
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('productDtails', product_id=products.id, product_slug=products.slug)  # Redirect to the same product page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()  # Create a new form instance

    
    # Fetch related images
    images = products.additional_images.all()

    # Calculate savings and discount percentage
    if products.price is not None:
        savings = products.price - (products.discount_amount or 0)
        discount_percentage = (savings / products.price * 100) if products.price else 0

    # Calculate sales message
    # Assuming last_sale_in_hours is a float or integer representing total hours
    # Increment views or last sale hours
    # Increment the view count
    products.increment_last_sale_in_hours()  

    # Prepare the sales message based on last_sale_in_hours
    if products.last_sale_in_hours >= 24:
        days = products.last_sale_in_hours // 24
        hours = products.last_sale_in_hours % 24
        
        if hours > 0:
            sales_message = f"{products.items_sold} sold in the last {days} days and {hours} hours"
        else:
            sales_message = f"{products.items_sold} sold in the last {days} days"
    else:
        sales_message = f"{products.items_sold} sold in the last {products.last_sale_in_hours} hours"

    # Use sales_message as needed
    print(sales_message)  # or pass it to the context for rendering in a template
            # Prepare context for rendering
    context = {
        'color':[pc.color_name for pc in product_color],
        'size':[pc.size for pc in product_color],
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
    }
    print(context)
    return render(request, 'shop/productDetail.html', context)




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
         
   
     