from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns =[
    path('register',views.RegisterView.as_view(),name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.Logout,name='logout'),
    path('dashboard/',views.Dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/',views.Activate,name='activate'),
    path('forgotPassword/',views.FogotPassword,name='forgotPassword'),
    path('resetPasswordValidation/<uidb64>/<token>/',views.ResetPasswordValidation,name='resetPasswordValidation'),
    path('resetPassword/',views.ResetPassword,name='resetPassword'),
]
