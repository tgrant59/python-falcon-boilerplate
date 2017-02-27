from app.utils import encryption

TEST_PASS = "password123"
BAD_GUESS = "badguess456"


def test_encrypt_password():
    encrypted_pass = encryption.encrypt_password(TEST_PASS)
    assert encrypted_pass != TEST_PASS  # Encrypts the Password

    encrypted_bad_guess = encryption.encrypt_password(BAD_GUESS, salt=encrypted_pass)
    assert encrypted_bad_guess != TEST_PASS  # Doesn't give plaintext password
    assert encrypted_bad_guess != BAD_GUESS  # Encrypts the Password
    assert encrypted_bad_guess != encrypted_pass  # Isn't correct password

    encrypted_good_guess = encryption.encrypt_password(TEST_PASS, salt=encrypted_pass)
    assert encrypted_good_guess != TEST_PASS  # Doesn't give plaintext password
    assert encrypted_good_guess == encrypted_pass  # Is correct password

    # Test without the password's salt given
    encrypted_good_guess = encryption.encrypt_password(TEST_PASS)
    assert encrypted_good_guess != TEST_PASS  # Doesn't give plaintext password
    assert encrypted_good_guess != encrypted_pass  # Is correct password, but without salt gives different result

    # Test with unicode password and salt
    encrypted_good_guess = encryption.encrypt_password(unicode(TEST_PASS), salt=unicode(encrypted_pass))
    assert encrypted_good_guess != TEST_PASS  # Doesn't give plaintext password
    assert encrypted_good_guess == encrypted_pass  # Is correct password


def test_generate_random_token():
    token = encryption.generate_random_token()
    assert token.isalnum()
    # Test that its different every time
    second_token = encryption.generate_random_token()
    assert token != second_token
