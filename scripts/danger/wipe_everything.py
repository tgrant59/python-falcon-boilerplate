import _load_app
from app.db import User
from app.db.documents import UserSettings
from app.utils import cache, documents


def main():
    yn = raw_input("This will remove EVERYTHING. This CANNOT BE UNDONE!!!!!!!! continue? (y/N)")
    if yn.lower() != "y":
        print "Aborting"
        exit(1)

    # ===== Tear Down =====
    # TODO: Make this drop the entire databases
    User.drop_table()  # DB
    documents.MDB.drop_collection(UserSettings.name)  # MongoDB
    for key in cache.RDB.keys("*"):  # Redis
        cache.RDB.delete(key)

    # ===== Setup =====
    User.create_table()  # DB


if __name__ == "__main__":
    main()
