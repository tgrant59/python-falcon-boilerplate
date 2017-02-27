import pymongo
import pytest
from bson import ObjectId
from app.utils import documents


class SimpleCollection(documents.Collection):
    name = "simple-collection"

    @staticmethod
    def new():
        return {
            "hello": 123
        }


@pytest.fixture(scope="module", autouse=True)
def collection():
    pymongo.collection.Collection(documents.MDB, SimpleCollection.name, create=True)
    yield
    documents.MDB.drop_collection(SimpleCollection.name)


@pytest.fixture
def document():
    doc_id = SimpleCollection.create(SimpleCollection.new())
    yield doc_id
    SimpleCollection.delete(doc_id)


# --------- Collection Tests --------
def test_create_collection():
    doc = SimpleCollection.new()
    doc_id = SimpleCollection.create(doc)
    result_doc = SimpleCollection.get(doc_id)
    assert "hello" in result_doc
    assert result_doc["hello"] == doc["hello"]
    SimpleCollection.delete(doc_id)


def test_get_collection(document):
    result_doc = SimpleCollection.get(document)
    assert "hello" in result_doc
    assert result_doc["hello"] == 123
    assert "_id" not in result_doc


def test_update_collection(document):
    new_doc = {
        "world": 456
    }
    SimpleCollection.update(document, new_doc)
    result_doc = SimpleCollection.get(document)
    assert "hello" not in result_doc
    assert "world" in result_doc
    assert result_doc["world"] == new_doc["world"]


def test_delete_collection():
    doc_id = SimpleCollection.create(SimpleCollection.new())
    SimpleCollection.delete(doc_id)
    result_doc = SimpleCollection.get(doc_id)
    assert result_doc is None


# --------- Helper Function Tests ----------
def test_format_str():
    assert documents.format_str("Hello") == "Hello"
    assert documents.format_str("Hello.world") == "Hello%@%world"
    assert documents.format_str("$Hello") == "#@#Hello"
    assert documents.format_str("$Hello.world") == "#@#Hello%@%world"


def test_format_dict():
    # Testing variations of nesting to make sure it gets all keys
    sample_dict = {
        "Hello": True,
        "Hello.com": "World",
        "$Hello": 666,
        "$Hello.world": [
            {
                "$Hello.world": {
                    "$Hello.world": True
                }
            },
            123
        ]
    }
    documents.format_dict(sample_dict)
    assert "Hello" in sample_dict
    assert "Hello%@%com" in sample_dict
    assert "#@#Hello" in sample_dict
    assert "#@#Hello%@%world" in sample_dict
    assert "#@#Hello%@%world" in sample_dict["#@#Hello%@%world"][0]
    assert "#@#Hello%@%world" in sample_dict["#@#Hello%@%world"][0]["#@#Hello%@%world"]
