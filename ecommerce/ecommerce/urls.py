"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from shop import views
from django.conf.urls.static import static
from django.conf import settings

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
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)