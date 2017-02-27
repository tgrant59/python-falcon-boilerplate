import json
import datetime
import pytest
from decimal import Decimal
from app.utils import helpers

TEST_DATETIME = datetime.datetime(2016, 9, 16, hour=8, minute=35, second=45)
TEST_DATETIME_STR = "2016-09-16 08:35:45"
TEST_DATE = datetime.date(2016, 9, 16)
TEST_DATE_STR = "2016-09-16"


def test_jsondumps():
    dic = {
        "Hello": "World",
        "int": 123,
        "float": 5.5,
        "decimal": Decimal(0.02),
        "datetime": TEST_DATETIME,
        "date": TEST_DATE,
        "list": [1, 2, 3, 4, 5],
        "dict": {
            "testing": 123
        }
    }
    json_dic = helpers.jsondumps(dic)
    assert isinstance(json_dic, str)
    unpacked_dic = json.loads(json_dic)
    assert "Hello" in unpacked_dic and "int" in unpacked_dic and "float" in unpacked_dic and \
           "decimal" in unpacked_dic and "datetime" in unpacked_dic and "date" in unpacked_dic and \
           "list" in unpacked_dic, "dict" in unpacked_dic
    assert unpacked_dic["Hello"] == "World"
    assert unpacked_dic["int"] == 123
    assert unpacked_dic["float"] == pytest.approx(5.5)
    assert unpacked_dic["decimal"] == pytest.approx(0.02)
    assert unpacked_dic["datetime"] == TEST_DATETIME_STR
    assert unpacked_dic["date"] == TEST_DATE_STR
    assert unpacked_dic["list"] == [1, 2, 3, 4, 5]
    assert unpacked_dic["dict"]["testing"] == 123


def test_strtobool():
    assert helpers.strtobool("True") is True
    assert helpers.strtobool("true") is True
    assert helpers.strtobool(u"True") is True
    assert helpers.strtobool("False") is False
    assert helpers.strtobool("false") is False
    assert helpers.strtobool(u"False") is False
    with pytest.raises(ValueError):
        helpers.strtobool(123)
    with pytest.raises(ValueError):
        helpers.strtobool("Hello, World!")


def test_strfdatetime():
    dt_str = helpers.strfdatetime(TEST_DATETIME)
    assert dt_str == TEST_DATETIME_STR


def test_strfdate():
    d_str = helpers.strfdate(TEST_DATE)
    assert d_str == TEST_DATE_STR


def test_strpdatetime():
    dt = helpers.strpdatetime(TEST_DATETIME_STR)
    assert dt == TEST_DATETIME
    with pytest.raises(ValueError):
        helpers.strpdatetime("Hello, World!")


def test_strpdate():
    d = helpers.strpdate(TEST_DATE_STR)
    assert d == TEST_DATE
    with pytest.raises(ValueError):
        helpers.strpdate("Hello, World!")


def test_chunk():
    l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    chunk_lengths = []
    for chunk in helpers.chunk(l, 3):
        chunk_lengths.append(len(list(chunk)))
    assert chunk_lengths == [3, 3, 3, 1]
