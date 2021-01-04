import os
import enum
from sqlalchemy import Column, String, create_engine, Integer, BigInteger, SmallInteger, Enum
from flask_sqlalchemy import SQLAlchemy
import json
import sys

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()


class RepositoryMixin:
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            print(sys.exc_info())
            return False
        finally:
            db.session.close()

    @classmethod
    def get_list_for_select(cls):
        records = cls.query.order_by(cls.name.asc()).all()
        return [(a.id, a.name) for a in records]


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Person
Have title and release year
'''


class Person(db.Model):
    __tablename__ = 'People'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    catchphrase = Column(String)

    def __init__(self, name, catchphrase=""):
        self.name = name
        self.catchphrase = catchphrase

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'catchphrase': self.catchphrase}


'''
Movie
Have title and release year
'''


class Movie(db.Model, RepositoryMixin):
    __tablename__ = 'Movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release = Column(BigInteger)
    crew = db.relationship('Crews', backref='Movies', lazy='joined')

    def __init__(self, title, release):
        self.title = title
        self.catchphrase = release

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release': self.release
        }


'''
Actor
Have name, age, and gender
'''


class GenderEnum(enum.Enum):
    Male = 1
    Female = 2
    Unspecified = 3


class Actor(db.Model, RepositoryMixin):
    __tablename__ = 'Actors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(SmallInteger)
    gender = Column(Enum(GenderEnum))
    crew = db.relationship('Crews', backref='Actors', lazy='joined')

    def __init__(self, name, age, gender=GenderEnum.Unspecified):
        self.name = name
        self.age = age
        self.gender = gender

    def format(self):
        return {
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }


class Crew(db.Model, RepositoryMixin):
    __tablename__ = 'Crews'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('Actors.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('Movies.id'))
    actor = db.relationship('Actors', lazy='joined')
    movie = db.relationship('Movies', lazy='joined')
