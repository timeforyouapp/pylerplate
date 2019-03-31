import datetime
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect


class Base():
    __table__ = None

    @declared_attr
    def __tablename__(self):
        if hasattr(self, '__table_name__'):
            return self.__table_name__

        return self.__name__.lower()

    query = None
    query_class = None

    id = Column(Integer, primary_key=True, autoincrement=True)

    deleted_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.now,
    )

    updated_at = Column(
        DateTime,
        onupdate=datetime.datetime.now,
        nullable=True,
    )

    def __iter__(self):
        _data = self.as_dict()
        return ((k, v) for k, v in _data.items())

    @classmethod
    def get_only_available(cls, q):
        return q.filter(cls.deleted_at.is_(None))

    @classmethod
    def get_all(cls, q=None):
        q = q or cls.query
        return cls.get_only_available(q).all()

    @classmethod
    def get(cls, _id, q=None):
        q = q or cls.query
        q = cls.get_only_available(q).filter(cls.id == _id)

        return q.first()

    def expunge(self):
        db.session.expunge(self)
        return self

    def save(self, flush=False, commit=False, call_validation=True):

        db.session.add(self)

        flush and db.session.flush()
        commit and self.commit()

        return self

    def merge(self):
        db.session.merge(self)
        return self

    def refresh(self):
        db.session.refresh(self)
        return self

    @staticmethod
    def rollback():
        db.session.rollback()

    @classmethod
    def commit(cls, flush=False):
        db.session.commit()
        flush and db.session.flush()

    def delete(self, commit=False, flush=False):
        self.deleted_at = datetime.datetime.now()

        self.save()
        if commit:
            self.commit(flush=flush)

    def as_dict(self, show_ids=True):
        data = {}
        for c in self.__table__.columns:

            if not show_ids and (
                c.name.strip() == inspect(self.__class__).primary_key[0].name
            ):
                continue

            if 'password' in c.name.lower():
                continue

            value = getattr(self, c.name)

            if isinstance(value, Decimal):
                value = float(value)

            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')

            data[c.name] = value

        return data


db = SQLAlchemy(model_class=Base)
