from datetime import timedelta


# ==== Generic ====
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
UTF8 = "utf8"

# ==== Authentication ====
# Cookies
AUTH_COOKIE_NAME = "session-id"
AUTH_CSRF_COOKIE_NAME = "csrf-token"
AUTH_CSRF_COOKIE_HTTP_ONLY = False
AUTH_COOKIE_EXPIRY_DELTA = timedelta(days=30)
AUTH_COOKIE_EXPIRY_SECONDS = 60*60*24*30  # 30 days

# ==== Users ====
# Roles
USER_ROLE_UNVERIFIED = "unverified"
USER_ROLE_UNPAID = "unpaid"
USER_ROLE_PAID = "paid"
USER_ROLE_CANCELLED = "cancelled"

# Assorted
USER_TRIAL_DAYS = 14

# ==== Redis ====
# Expiration times
REDIS_EXPIRY_EMAIL_VERIFICATION = 60*60*24*7  # One week
REDIS_EXPIRY_PASSWORD_RESET = 60*20  # 20 mins

# ==== Mongo ====
MONGO_DOT_PLACEHOLDER = "||dot||"
MONGO_DOLLAR_PLACEHOLDER = "||dollar||"
