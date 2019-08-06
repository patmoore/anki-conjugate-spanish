from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import MetaData

from conjugate_spanish.database.session import add_to_session, commit_session

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

meta = MetaData(naming_convention=convention)

class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)

    @classmethod
    def create(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        add_to_session(obj)
        commit_session()
        return obj


BASE = declarative_base(cls=BaseModel, metadata=meta)