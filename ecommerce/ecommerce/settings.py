# Import dj-database-url at the beginning of the file.
# import dj_database_url
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

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    
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
    'Api_APP',
    'promotions',
    
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


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # or your DB engine
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', default='5432'),  # Set a default if needed
    }
}

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
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