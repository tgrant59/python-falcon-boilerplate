import peewee as p
from playhouse.hybrid import hybrid_property
from app.db import BaseModel, lazy_property
from app.db.documents import UserSettings
from app.utils import cache


class User(BaseModel):
    email = p.CharField(index=True, unique=True)
    first_name = p.CharField()
    last_name = p.CharField()
    password = p.CharField()
    role = p.CharField()
    created = p.DateTimeField()
    stripe_id = p.CharField(index=True, null=True, unique=True)
    _settings_id = p.CharField()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        cache.update_all_sessions(self)

    def to_dict(self, **kwargs):
        user_dict = super(User, self).to_dict(**kwargs)
        user_dict["full_name"] = self.full_name
        del user_dict["_settings_id"]
        del user_dict["stripe_id"]
        user_dict["settings"] = self.settings
        return user_dict

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name

    @full_name.expression
    def full_name(self):
        return p.fn.CONCAT_WS(" ", self.first_name, self.last_name)

    @lazy_property
    def settings(self):
        return UserSettings.get(self._settings_id)

    def save_settings(self):
        UserSettings.update(self._settings_id, self.settings)
        cache.update_all_sessions(self)


class CachedUser(object):
    """
    This class cannot be used to modify the user or their settings. If you need to modify the user, get the true
    user model by using the from_db() function
    """
    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.email = user_dict["email"]
        self.first_name = user_dict["first_name"]
        self.last_name = user_dict["last_name"]
        self.full_name = user_dict["full_name"]
        self.password = user_dict["password"]
        self.role = user_dict["role"]
        self.settings = user_dict["settings"]

    def from_db(self):
        return User.get(User.id == self.id)

    def to_dict(self):
        return self.__dict__
