import pymongo
from bson.objectid import ObjectId
from app.utils import config, constants

MONGO_CLIENT = pymongo.MongoClient("mongodb://{user}:{password}@{host}:{port}/?authSource={authSource}".format(
    user=config.MONGO_USER,
    password=config.MONGO_PASSWORD,
    host=config.MONGO_HOST,
    port=config.MONGO_PORT,
    authSource=config.MONGO_AUTH_DB
))
MDB = MONGO_CLIENT[config.MONGO_DB]


class Collection(object):
    """
    Extend this class, assign a name attribute, and define a new method to create a new collection
    """
    name = None

    @classmethod
    def create(cls, doc):
        new_doc = MDB[cls.name].insert_one(doc)
        # inserted_id returns an ObjectId instance, but we need the unicode representation
        return unicode(new_doc.inserted_id)

    @classmethod
    def get(cls, doc_id):
        doc = MDB[cls.name].find_one({"_id": ObjectId(doc_id)})
        if doc is not None:
            del doc["_id"]
        return doc

    @classmethod
    def update(cls, doc_id, new_doc):
        doc_id = ObjectId(doc_id)
        # A shallow copy is fine, because we are only adding the base level "_id" attribute
        new_doc = new_doc.copy()
        new_doc["_id"] = doc_id
        MDB[cls.name].replace_one({"_id": doc_id}, new_doc, upsert=True)

    @classmethod
    def delete(cls, doc_id):
        MDB[cls.name].delete_one({"_id": ObjectId(doc_id)})


# ------------- Functions ---------------
def format_str(string):
    new_string = string.replace(".", constants.MONGO_DOT_PLACEHOLDER)
    new_string = new_string.replace("$", constants.MONGO_DOLLAR_PLACEHOLDER)
    return new_string


def format_dict(dic):
    """
    Modifies dic in place
    """
    keys_to_change = []
    for key, value in dic.items():
        if "." in key or "$" in key:
            keys_to_change.append(key)
        if isinstance(value, dict):
            format_dict(value)
        elif isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict):
                    format_dict(entry)
    for key in keys_to_change:
        new_key = key.replace(".", constants.MONGO_DOT_PLACEHOLDER)
        new_key = new_key.replace("$", constants.MONGO_DOLLAR_PLACEHOLDER)
        dic[new_key] = dic.pop(key)
