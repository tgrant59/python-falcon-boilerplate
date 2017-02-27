import datetime
import falcon
from app.db import User
from app.db.documents import UserSettings
from app.async import mailer
from app.utils import cache, constants, encryption, payment


def create_user(email, hashed_password, first_name, last_name):
    user_settings = UserSettings.new()
    user_settings["account"]["created"] = datetime.datetime.utcnow()
    user_settings_id = UserSettings.create(user_settings)
    new_user = User.create(email=email,
                           first_name=first_name,
                           last_name=last_name,
                           password=hashed_password,
                           role=constants.USER_ROLE_UNVERIFIED,
                           created=datetime.datetime.utcnow(),
                           _settings_id=user_settings_id)
    stripe_metadata = {
        "user_id": new_user.id
    }
    customer = payment.create_customer(new_user.email, stripe_metadata)
    new_user.stripe_id = customer["id"]
    new_user.save()
    mailer.welcome.delay(new_user.id)
    return new_user


def change_name(user, first_name, last_name):
    """
    Make sure you pass this function the DB user
    """
    user.first_name = first_name
    user.last_name = last_name
    user.save()


def change_password(user, current_password, new_password):
    """
    Make sure you pass this function the DB user
    """
    if encryption.encrypt_password(current_password, salt=user.password) != user.password:
        raise falcon.HTTPBadRequest("Incorrect Password", "Current password is incorrect")
    new_hashed_password = encryption.encrypt_password(new_password)
    user.password = new_hashed_password
    user.save()


def forgot_password(email):
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        raise falcon.HTTPBadRequest("User Not Found", "No user was found with that email address")
    reset_token = encryption.generate_random_token()
    cache.set_password_reset_token(user, reset_token)
    mailer.password_reset.delay(user.id, reset_token)


def reset_password(new_password, reset_token):
    user_id = cache.get_user_id_by_password_reset_token(reset_token)
    if user_id is None:
        raise falcon.HTTPBadRequest("Invalid Token", "Password reset token is invalid or expired")
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        raise falcon.HTTPBadRequest("User Not Found",
                                    "The user associated with the password reset token cannot be found")
    new_hashed_password = encryption.encrypt_password(new_password)
    user.password = new_hashed_password
    user.save()
    cache.remove_all_sessions(user)
    cache.remove_password_reset_token(reset_token)


def new_verification_email(user):
    if user.role != constants.USER_ROLE_UNVERIFIED:
        raise falcon.HTTPBadRequest("Email Already Verified", "The user's email address has already been verified")
    else:
        verification_token = encryption.generate_random_token()
        cache.set_email_verification_token(user, verification_token)
        mailer.email_verification.delay(user.id, verification_token)


def verify_email(verification_token):
    user_id = cache.get_user_id_by_email_verification_token(verification_token)
    if user_id is None:
        raise falcon.HTTPBadRequest("Invalid Token", "Email verification token is invalid or expired")
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        raise falcon.HTTPBadRequest("User Not Found",
                                    "The user associated with the password reset token cannot be found")
    user.role = constants.USER_ROLE_UNPAID
    user.save()
    cache.remove_email_verification_token(verification_token)


def send_feedback(user, feedback):
    mailer.feedback.delay(user.id, feedback)


def unsubscribe(user_id, email):
    # This is because we use a Mock user with id 0 for admin emails, but the email template requires an id
    if user_id == 0:
        return
    try:
        user = User.get(User.id == user_id, User.email == email)
    except User.DoesNotExist:
        raise falcon.HTTPBadRequest("User Not Found",
                                    "A user associated with the given id and email cannot be found")
    user.settings["notifications"]["unsubscribe"] = True
    user.save_settings()
