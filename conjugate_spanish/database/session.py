import os

from conjugate_spanish.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy_searchable import make_searchable

from functools import wraps
from contextlib import contextmanager


if os.environ.get('API_TESTING') == '1':
    ENGINE = create_engine(settings.SQL_TESTING_URI, pool_recycle=3600)
else:
    ENGINE = create_engine(settings.SQL_URI, pool_recycle=3600, echo=settings.ECHO_SQL)

SESSION_MAKER = sessionmaker()
SESSION_MAKER.configure(bind=ENGINE)

SESSION = None


def start_session():
    global SESSION
    SESSION = SESSION_MAKER(autocommit=False,
                            autoflush=False,
                            bind=ENGINE)

start_session()

# make_searchable()


def get_session():
    """
    used in other files, since importing SESSION fails in weird edge cases
    """
    return SESSION


@contextmanager
def closing_session():  # implemented this way because of our implementation of SESSION above
    try:
        if not os.environ.get('API_TESTING'):
            SESSION.close()  # for good measure
        yield SESSION
    finally:
        if not os.environ.get('API_TESTING'):
            SESSION.close()


def with_closing_session(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        with closing_session():
            return original_function(*args, **kwargs)

    return wrapper


def add_to_session(objects):
    from collections import Iterable
    if isinstance(objects, Iterable):
        for object in objects:
            SESSION.add(object)
    else:
        SESSION.add(objects)


def commit_session():
    SESSION.commit()


def close_session():
    SESSION.close()
