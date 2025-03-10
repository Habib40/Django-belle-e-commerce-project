from django.db import models
from category.models import Category
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
from account.models import Account
from order.models import Order,OrderProduct


# Define product labels
LABELS = (
    ('new', 'New'),
    ('sale', 'Sale'),
    ('best_selling', 'Best Selling'),
)

# Define a tuple of color names
COLORS = (
    ('red', 'Red'),
    ('green', 'Green'),
    ('blue', 'Blue'),
    ('yellow', 'Yellow'),
    ('purple', 'Purple'),
    ('orange', 'Orange'),
    ('black', 'Black'),
    ('white', 'White'),
    ('pink', 'Pink'),
    ('gray', 'Gray'),
    ('cyan', 'Cyan'),
    ('magenta', 'Magenta'),
    ('brown', 'Brown'),
    ('lime', 'Lime'),
    ('navy', 'Navy'),
    ('teal', 'Teal'),
    ('violet', 'Violet'),
    ('coral', 'Coral'),
    ('salmon', 'Salmon'),
)
# Define a tuple of size options
SIZES = (
    ('xs', 'Extra Small'),
    ('s', 'Small'),
    ('m', 'Medium'),
    ('l', 'Large'),
    ('xl', 'Extra Large'),
    ('xxl', 'Double Extra Large'),
    ('3xl', 'Triple Extra Large'),
    ('4xl', 'Quadruple Extra Large'),
)

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True) 
    related_products = models.ManyToManyField('self', symmetrical=False, related_name='related_to', blank=True)# Self-referential many-to-many relationship
    images = models.ImageField(upload_to='products/')
    hoverImg = models.ImageField(upload_to='hover_images/', null=True, blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    sku = models.CharField(max_length=100, unique=True)
    ratings_count = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity_sold = models.PositiveIntegerField(default=0)
    quantity_left = models.PositiveIntegerField(default=0)
    video_url = models.URLField(max_length=200, null=True, blank=True)
    labels = models.CharField(max_length=40, choices=LABELS)
    stock = models.IntegerField()
    items_sold = models.IntegerField(default=0)
    last_sold_time = models.DateTimeField(auto_now=True,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.price and self.discount_amount:
            if self.discount_amount > self.price:
                raise ValidationError("Discount amount cannot be greater than the price.")
            self.discount_percentage = round((self.price - self.discount_amount) / self.price * 100)
        else:
            self.discount_percentage = 0

        super().save(*args, **kwargs)
    

    def get_image_url(self):
        return self.images.url
    
    def get_url(self):
      return reverse('productDetails', args=[self.category.slug,self.slug])

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, choices=SIZES, default='m', unique=False)
    color_name = models.CharField(max_length=50, choices=COLORS)
    
    class Meta:
        verbose_name = 'Product Color'  # Singular form
        verbose_name_plural = 'Product Colors And Sizes'  # Plural form
    def __str__(self):
        return f"{self.color_name} ({self.size})"




class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author_name}"


@receiver(post_save, sender=Review)
def update_ratings_count(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.ratings_count += 1
        product.save()  # Add unique=True if needed
    
   


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/additional_images/')
    thumbnail = models.ImageField(upload_to='products/thumbnails/', null=True, blank=True)

    def __str__(self):
        return f'Image for {self.product.title}'

class WishList(models.Model):
    user =models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    wish_product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    
    
    def __str__(self):
        return f"{self.user.username}'s wishlist -{self.wish_product.title}"
    
    class Meta:
        verbose_name = 'Wish List' # Singular form
        


    

        
        
    