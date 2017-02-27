import pytest
from app.core import user_core
from app.utils import encryption, payment

USER_EMAIL = "user@example.com"
USER_PASSWORD = "password123"
USER_FIRST_NAME = "David"
USER_LAST_NAME = "Bowie"


@pytest.fixture
def user(monkeypatch):
    def payment_create_customer_patch(_, __):
        return {"id": encryption.generate_random_token()}
    monkeypatch.setattr(payment, "create_customer", payment_create_customer_patch)
    encrypted_pass = encryption.encrypt_password(USER_PASSWORD)
    new_user = user_core.create_user(USER_EMAIL, encrypted_pass, USER_FIRST_NAME, USER_LAST_NAME)
    yield new_user
