from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hxh%w6ctynfa8^cg$wo!fdn=bz7z=6x5(m_w)h9slyan4e3dpl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'main',
    'rest_framework',
    'rest_framework.authtoken',
    #sms send
    'django_crontab',
    
    'import_export',
    'django.contrib.humanize'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'domstroy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'domstroy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'OPTIONS': {
#            'read_default_file':'/var/www/bordo/auth/mysql.cnf'
#        }
#    }
#}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
    ),
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S"
}

CRONJOBS = [
    # ('0 12 * * 1-6', 'main.views.schedular_sms_send'), #At 12:00 on every day-of-week from Monday through Saturday. bir sms jo'natadi qarz kui kelganlarga
    # ('0 14 * * 1-6', 'main.views.schedular_sms_send_olds'), #At 14:00 on every day-of-week from Monday through Saturday bir sms jo'natadi Qarzi utib ketganlarga
    
    ('0 */6 * * *', 'main.views.schedular_sms_send'), #6sotda. bir sms jo'natadi qarz kui kelganlarga
    ('0 */7 * * *', 'main.views.schedular_sms_send_olds'), #7 sotda bir sms jo'natadi Qarzi utib ketganlarga
    ('0 */8 * * *', 'main.views.schedular_sms_send_alert'), #8 sotda bir sms jo'natadi Qarzi utib ketganlarga

    # ('*/1 * * * *', 'main.views.schedular_sms_send'),  # 1 min bir sms jo'natadi test qarz kui kelganlarga
    # ('*/2 * * * *', 'main.views.schedular_sms_send_olds')  # 2 min bir sms jo'natadi test old
   

]

#Qarzini  tulaganida    sms jo'natadi

# RETURN_DEBTOR_SMS = "Qarzini berdi"
RETURN_DEBTOR_SMS = '''
Assalom alaykum xurmatli {name} siz {som} so'm to'lov amalga oshirdingizni ma'lum qilamiz 
Qoldiq summa {qoldi} sum
Xurmat bilan Bordo jamoasi dokoni

Murojaat uchun: +998901254042
'''

#Qarziniga olsa sms jo'natadi
GET_DEBTOR_SMS = 'Assalom alaykum xurmatli {name} siz Bordo jamoasi dokonidan {som} so\'m qarzdor bo\'lganingizni ma\'lum qilamiz. To\'lov muddati {kun} gacha belgilandi, tolovni kechiktirmaysiz degan umitdamiz. Siz bilan hamkorlik qilayotganimizidan hursandmiz. Xurmat bilan Bordo jamoasi dokoni Murojat uchun:  +998901254042 '

#Deadline sms
DEADLINE_SMS = "Qarz vaqti keldi"

# Qarz kunidan utib ketdi
OLD_DEADLINE_SMS = '''
Assalom alaykum xurmatli mijoz sizni Bordo jamoasi do'konidagi QARZ muomilangiz muddati utib ketganini malum qilamiz, iltimos tulovni amalga oshiring.
Bu orqali siz, hamkorligimizni uzoq davom etishini taminlagan bo'lasiz.
Xurmat bilan Bordo jamoasi dokoni!

    Murojat uchun:
    +998901254042
'''

#3day ago alert sms
THREE_DAY_AGO_SMS = '''
Assalom alaykum xurmatli {name} sizni tulov muddatingizga 3 kun qolganini eslatib utamiz
Iltimos tulovni kechiktirmay amalga oshirishingizni suraymiz!!!
Summa {som} so'm

Xurmat bilan Bordo jamoasi!

Murojat uchun: +998901254042
'''

# CRONTAB_COMMAND_SUFFIX = '2>&1'
LANGUAGE_CODE = 'uz-uz'

TIME_ZONE = 'Asia/Tashkent'

#DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/login'

#sms
SMS_EMAIL = 'abdullox19990604@gmail.com'
SMS_SECRET_KEY = 'dfSkYkW7ypJdJHUhTdNJbOA1EIIddzTToUoJ5blJ'
SMS_BASE_URL = 'http://notify.eskiz.uz'
SMS_TOKEN = ''

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'assets'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ALLOWED_ORIGINS = [
    "http://104.236.200.53"
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'token',
    'x-device-id',
    'x-device-type',
    'x-push-id',
    'dataserviceversion',
    'maxdataserviceversion'
)
CORS_ALLOW_METHODS = (
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS'
    )
