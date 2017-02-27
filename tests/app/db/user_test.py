from app.db import User, CachedUser


# ===== User Tests =====
def test_to_dict(user):
    user_dict = user.to_dict()
    assert user_dict["id"] == user.id
    assert user_dict["full_name"] == user.full_name
    assert "_settings_id" not in user_dict
    assert "settings" in user_dict
    assert isinstance(user_dict["settings"], dict)
    assert "stripe_id" not in user_dict


def test_full_name(user):
    expected_full_name = user.first_name + " " + user.last_name
    assert user.full_name == expected_full_name
    user_by_full_name = User.get(User.full_name == expected_full_name)
    assert user_by_full_name.id == user.id


def test_settings(user):
    assert isinstance(user.settings, dict)


def test_save_settings(user):
    user.settings["testsetting"] = "testvalue"
    user_double = User.get(User.id == user.id)
    assert "testsetting" not in user_double.settings
    user.save_settings()
    user_double = User.get(User.id == user.id)
    assert user_double.settings["testsetting"] == "testvalue"


# ===== Cached User Tests =====
def test_cached_user_init(user):
    cached_user = CachedUser(user.to_dict())
    assert cached_user.id == user.id
    assert cached_user.full_name == user.full_name
    assert cached_user.settings == user.settings
    assert not hasattr(cached_user, "_settings_id")
    assert not hasattr(cached_user, "stripe_id")


def test_cached_user_from_db(user):
    cached_user = CachedUser(user.to_dict())
    db_user = cached_user.from_db()
    assert db_user.id == user.id
