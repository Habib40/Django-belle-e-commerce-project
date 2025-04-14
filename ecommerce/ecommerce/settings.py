# Import dj-database-url at the beginning of the file
import dj_database_url
from pathlib import Path
import os
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

# Load environment variables from .env file
load_dotenv()
# Access environment variables
STEADFAST_API_KEY = os.getenv("STEADFAST_API_KEY")
STEADFAST_SECRET_KEY = os.getenv("STEADFAST_SECRET_KEY")
STEADFAST_BASE_URL = os.getenv("STEADFAST_BASE_URL")
APIK_KEY = f"This is APIKEY  {STEADFAST_API_KEY} from SteadFast"

# STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
# STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
IT_PAY_BD_API_KEY = os.getenv("IT_PAY_BD_API_KEY")
# print(f"This is STRIPE_PUBLISHABLE_KEY " ,STRIPE_PUBLISHABLE_KEY)
# print(f"This is STRIPE_SECRET_KEY ",STRIPE_SECRET_KEY)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = BASE_DIR/'templates'
TEMPLATE = TEMPLATES_DIRS

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ['https://django-belle-e-commerce-project-5.onrender.com']


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'category',
    'cart',
    'order',
    'account',
    'blog',
    'Api_APP',
    'promotions',
    'customApp',
    'tinymce',
    
]

MIDDLEWARE = [
 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'customApp.middleware.middleware.Custom404Middleware', # Custom middleware for 404 error page
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_context',  # Add your context processor here
                'category.context_processors.menue_links',
                'shop.context_processors.wishlist_items',
            ],
        },
    },
]


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# # Get the WSGI application for the project.
# application = get_wsgi_application()

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# for custom user table in admin panel
AUTH_USER_MODEL = 'account.Account'


# Determine which database configuration to use
# DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'local')  # Default to 'local' if not set

# Use local PostgreSQL database configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # or your DB engine
#         'NAME': os.getenv('DATABASE_NAME'),
#         'USER': os.getenv('DATABASE_USER'),
#         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
#         'HOST': os.getenv('DATABASE_HOST'),
#         'PORT': os.getenv('DATABASE_PORT', default='5432'),  # Set a default if needed
#     }
# }


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# # # Database configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # or your DB engine
#         'NAME': os.getenv('DATABASE_NAME'),
#         'USER': os.getenv('DATABASE_USER'),
#         'PASSWORD': os.getenv('DATABASE_PASSWORD'),
#         'HOST': os.getenv('DATABASE_HOST'),
#         'PORT': os.getenv('DATABASE_PORT', default='5432'),  # Set a default if needed
#     }
# }

# DATABASES['default'] = dj_database_url.parse(os.getenv('DATABASE_URL'))

# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mysite'),
#         conn_max_age=600
#     )
# }
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Dhaka'


USE_I18N = True

USE_TZ = True
# Django-SimpleUi Configuration
SIMPLEUI_HOME_INFO = False 
SIMPLEUI_ANALYSIS = False 
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'
SIMPLEUI_DEFAULT_THEME = 'element.css'
SIMPLEUI_DEFAULT_THEME = 'layui.css'
SIMPLEUI_DEFAULT_THEME = 'purple.css'
# replace default Logo image
SIMPLEUI_LOGO = '/static/assets/images/logo.svg'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/



STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'  # URL prefix for accessing media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

# if not DEBUG:
#     # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'habibkb5080@gmail.com'
EMAIL_HOST_PASSWORD = 'fgzzzljvhqrnctkn'

PASSWORD_RESET_TOKEN_GENERATOR = 'django.contrib.auth.tokens.PasswordResetTokenGenerator'



ALLOWED_HOSTS = ['*']

# Also add CSRF settings
CSRF_TRUSTED_ORIGINS = ['https://*', 'http://*']  # Be more specific in production
CORS_ALLOW_ALL_ORIGINS = True  # For django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True

# Tinymce settings
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'silver',  # Theme can be 'silver', 'modern', etc.
    'height': 400,  # Increased height for better visibility
    'width': 800,  # Width of the editor
    'plugins': 'link image code lists table paste help',  # Additional plugins
    'images_upload_url': '/tinymce/upload/',  # URL for image uploads
    'automatic_uploads': True,  # Automatically upload images
    'file_picker_types': 'image',  # Allow only images in the file picker
    'toolbar': 'undo redo | styleselect | bold italic | underline | forecolor backcolor | alignleft aligncenter alignright | bullist numlist outdent indent | link image | code | help',  # Custom toolbar layout
    'toolbar_location': 'top',  # Position of the toolbar
    'relative_urls': False,  # Use absolute URLs
    'remove_script_host': False,  # Keep the host in URLs
    'convert_urls': True,  # Convert URLs
    'content_css': '/static/css/content.css',  # Path to custom CSS for the content
    'file_picker_callback': 'function(callback, value, meta) { /* Custom file picker */ }',  # Custom file picker function
    'branding': False,  # Disable branding
    'statusbar': False,  # Hide the status bar
    'menubar': False, # Disable the menubar
}

# # settings.py
# TINYMCE_DEFAULT_CONFIG = {
#     'theme': 'silver',
#     'height': 400,
#     'width': 800,
#     'plugins': 'link image code lists table paste help',
#     'toolbar': 'undo redo | styleselect | bold italic | underline | forecolor backcolor | alignleft aligncenter alignright | bullist numlist outdent indent | link image | code | help',
    
#     'menubar': False, # Disable the menubar
#     'toolbar_items_size': 'small', # Make the toolbar items smaller
#     'branding': False,  # Disable branding
#     'statusbar': False,  # Hide the status bar
#     'object_resizing': 'true',  # Enable object resizing
# }