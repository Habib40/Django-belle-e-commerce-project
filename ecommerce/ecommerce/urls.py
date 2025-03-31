
from django.contrib import admin
from django.urls import path,include
from shop import views
from django.conf.urls.static import static
from django.conf import settings
admin.site.site_header = 'Belle E-commerce Admin'
admin.site.site_title = 'Belle E-commerce Admin'
admin.site.index_title = 'Belle E-commerce Admin'
# admin.site.site_url = ''

# Now register your models with this custom admin site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.Index,name='index'),
    path('load/', views.LoadProducts),
    path('details/<int:product_id>/',views.ProductDetail,name='productDtails'),
    path('cat/',include('category.urls')),
    path('store/', include('shop.urls')),
    path('carts/', include('cart.urls')),
    path('accounts/', include('account.urls')),
    path('', include('Api_APP.urls')),
    # orders paths
    path('orders/',include('order.urls'))
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
