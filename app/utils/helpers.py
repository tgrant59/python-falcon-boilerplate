import datetime
import json
import signal
import itertools
from contextlib import contextmanager
from decimal import Decimal
from app.utils import constants, errors


def _custom_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return strfdatetime(obj)
    elif isinstance(obj, datetime.date):
        return strfdate(obj)
    elif isinstance(obj, Decimal):
        return float(obj)


def jsondumps(obj):
    return json.dumps(obj, default=_custom_encoder)


def strtobool(string):
    """
    Returns bool or raises ValueError so as to be usable directly in voluptuous validation
    """
    if not isinstance(string, (str, unicode)):
        raise ValueError
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        raise ValueError


def strfdatetime(datetime_obj):
    return datetime_obj.strftime(constants.DEFAULT_DATETIME_FORMAT)


def strfdate(date_obj):
    return date_obj.strftime(constants.DEFAULT_DATE_FORMAT)


def strpdatetime(datetime_str):
    """
    Returns datetime or raises ValueError so as to be usable directly in voluptuous validation
    """
    return datetime.datetime.strptime(datetime_str, constants.DEFAULT_DATETIME_FORMAT)


def strpdate(date_str):
    """
    Returns date or raises ValueError so as to be usable directly in voluptuous validation
    """
    return datetime.datetime.strptime(date_str, constants.DEFAULT_DATE_FORMAT).date()


def chunk(iterable, n):
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)
