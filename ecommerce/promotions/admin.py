from django.contrib import admin
from .models import Promotion,AppliedPromotion
# Register your models here.
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage')
    search_fields = ('code','discount_percentage')
admin.site.register(Promotion, PromotionAdmin),
admin.site.register(AppliedPromotion)