from app.utils import documents


class UserSettings(documents.Collection):
    name = "user_settings"

    @staticmethod
    def new():
        return {
            "account": {
                "plan": None,
                "num_users": 1,
                "had_trial": False
            },
            "notifications": {
                "unsubscribe": False
            }
        }
