from django.contrib import admin
from .models import Product,ProductColor,ProductImage,Review
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.core.exceptions import ValidationError

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0  # Set to 0 to avoid displaying empty forms for new images
class ProductColorInLine(admin.TabularInline):
    model = ProductColor
    extra = 0  # Set to 0 to avoid displaying empty forms for new images
    fields = ('color_name', 'size')
    readonly_fields = ('get_color_preview',)  # Make the preview read-only

    def get_color_preview(self, obj):
        # Assuming you have a method or property to get a color preview
        return f"<div style='width: 20px; height: 20px; background-color: {obj.color_name};'></div>"
    
    get_color_preview.allow_tags = True  # Allow HTML in the admin
    get_color_preview.short_description = 'Color Preview'  # Custom label for the field

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline,ProductColorInLine]  # Include inline for managing product images
     
    
    list_display = ('title', 'show_image', 'price', 'is_available', 'created_at')  # Use show_image to display image
    readonly_fields = ('discount_percentage',)  # Keep discount_percentage read-only
    prepopulated_fields = {'slug': ('title',)}  # Automatically generate slug from title
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'images', 'hoverImg', 'sku', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_amount', 'compare_price', 'quantity_sold', 'quantity_left', 'stock')
        }),
        ('Sales Data', {
            'fields': ('items_sold', 'last_sale_in_hours','last_sale_time','labels')
        }),
        ('Related Products', {
            'fields': ('related_products',)
        }),
    )
    def show_image(self, obj):
        if obj.images:
            # Display the product image as a thumbnail
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.images.url)
        return "No Image"  # Fallback if no image is found

    show_image.short_description = 'Image'  # Column name in the admin list view
   
    def save_model(self, request, obj, form, change):
        try:
            # Save the object first to ensure it has an ID
            super().save_model(request, obj, form, change)

            # Now handle the many-to-many relationship
            if 'related_products' in form.cleaned_data:
                obj.related_products.set(form.cleaned_data['related_products'])

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, 'An error ocured')
            return  # Prevent saving the invalid object
    
# Register the Product model with the custom admin class
admin.site.register(Product, ProductAdmin)



class ReviewAdmin(admin.ModelAdmin):
    list_display=['product','author_name','author_email','body','rating']
    list_filter=['product','author_name','author_email','body','rating']
    list_per_page=50
    list_display_links=['product','author_name','author_email','body','rating']
    search_fields = ['author_name', 'author_email', 'body']
    ordering = ['-rating']
    actions = ['mark_as_approved']

    
admin.site.register(Review,ReviewAdmin)

def mark_as_approved(self, request, queryset):
    # Logic to mark reviews as approved
    self.message_user(request, "Selected reviews have been marked as approved.")

