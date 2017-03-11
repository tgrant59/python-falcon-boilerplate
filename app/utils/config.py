import os
import pytz


# Use environment variables for any variables that:
# 1. Change per developer
# 2. Need high security in production

# ======= General config ========
ENVIRONMENT = 'development'
REPO_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../'
TIMEZONE = pytz.timezone('America/Toronto')
FRONTEND_HOST = 'http://localhost:7000'

# ========== Authentication config ===========
AUTH_BCRYPT_ROUNDS = 4  # Should be at least 12 in production
AUTH_COOKIE_DOMAIN = None
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_HTTP_ONLY = False
AUTH_COOKIE_SECURE = False

# ========== Headers config ============
# --- Headers in the form of (name, value) tuples ---
RESPONSE_HEADERS = [
    # Enable this line if you choose to add your domain to the HSTS preload list
    # ('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload'),
    ('Content-Type', 'application/json'),
    ('Frame-Ancestors', 'none'),  # Frame header is for anti-clickjacking protection
    ('Cache-Control', 'no-cache,no-store'),  # So browsers never cache the API requests
    ('Access-Control-Allow-Origin', FRONTEND_HOST),
    ('Access-Control-Allow-Headers', 'accept, content-type'),
    ('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS'),
    ('Access-Control-Allow-Credentials', 'true'),
    ('Access-Control-Max-Age', '86400')
]

# ============ Email config =============
# The address which receives all emails when not in production
EMAIL_TESTING_ADDRESS = os.environ['DEV_EMAIL']
EMAIL_TEMPLATE_PATH = REPO_PATH + 'email_templates/'
# The email addresses that emails to users are sent from
EMAIL_NO_REPLY_ADDRESS = 'Example Corp. <no-reply@example.com>'
EMAIL_INFO_ADDRESS = 'Example Corp. <info@example.com>'
EMAIL_ADMIN_ADDRESS = 'Admin at Example Corp. <admin@example.com>'

# =========== AWS config ==========
AWS_REGION = 'us-east-1'

# =========== Redis config ==========
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = os.environ['REDIS_DB']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_URI = 'redis://:{password}@{host}:{port}/{db}'.format(
    password=REDIS_PASSWORD, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB
)

# ========== MySQL config ===========
MYSQL_DB_NAME = os.environ['MYSQL_DB']
MYSQL_HOST = 'mysql'
MYSQL_PORT = 3306
MYSQL_SSL = None
MYSQL_MAX_CONNECTIONS = 256
MYSQL_STALE_TIMEOUT = 300  # 5 minutes
MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']

# ========= Peewee config ==========
PEEWEE_LOGGING = False

# ========= MongoDB config ==========
MONGO_HOST = 'mongo'
MONGO_PORT = 27017
MONGO_DB = os.environ["MONGO_DB"]
MONGO_USER = os.environ['MONGO_USER']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
MONGO_AUTH_DB = 'admin'

# ========= Sentry.io config =========
SENTRY_DNS = os.environ['SENTRY_DNS']

# ========= Celery config ==========
CELERY_CONFIG = {
    'broker_url': REDIS_URI,
    'result_backend': REDIS_URI,
    'worker_pool_restarts': True,
    'timezone': 'America/Toronto',
    'broker_transport_options': {
        'fanout_prefix': True,
        'fanout_patterns': True
    }
}

# =========== Stripe config ===========
STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_KEY']
STRIPE_CURRENCY = 'usd'
STRIPE_PLANS = {
    'example-plan-name': {'plan-metadata': 'example'}
}
STRIPE_TRIAL_PLANS = ['example-plan-name']
