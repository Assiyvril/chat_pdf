"""
Django settings for GPT project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from common import jwt_login
print('hello world')
import openai

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lmrgwy%)03mixj=0sf&rxi56pat52(8(t2y$6$yb_r5agp%fk1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'uploader',
    'user',
    'rest_framework',
    'rest_framework.authtoken',
    'chat_history',
    'corsheaders',
    'common',
    "rest_framework_jwt"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",    # 跨域中间件
    "django.middleware.common.CommonMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'GPT.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GPT.wsgi.application'
# ASGI_APPLICATION = 'GPT.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'gpt',  # 数据库名，先创建的
        'USER': 'root',  # 用户名，可以自己创建用户
        'PASSWORD': 'hello',  # 密码
        'HOST': '127.0.0.1',  # mysql服务所在的主机ip
        'PORT': '3306',  # mysql服务端口
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# 登录认证

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'common.custom_jwt.CustomJWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',  # 不用这个，卸载掉，一会添加客制化 JWT
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT认证
from datetime import timedelta
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(seconds=24 * 3600),
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_AUTH_COOKIE': "token",
    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'common.custom_jwt.jwt_response_payload_handler',   # TODO 一会写完来修改
}

# 0401， 11：23 添加
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 项目根目录

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 上传文件保存目录
UP_FILE_DIR = os.path.join(ROOT_DIR, 'UpFileDir')

# openai api key
OPEN_AI_API_KEY = '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'

# 本地代理端口, HTTP
LOCAL_PROXY = '127.0.0.1:10809'

# GCS 存储pdf文件的bucket
GCS_PDF_BUCKET = 'gpt_demo'

# Google Cloud Key 文件
GOOGLE_KEY_FILE = os.path.join(ROOT_DIR, 'GPT', 'googlekey.json')

