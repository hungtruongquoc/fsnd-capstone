import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase, mock
from functools import wraps
from datetime import timezone
import datetime

from models import setup_db, Actor, GenderEnum, Movie, Crew, db


def get_utc_timestamp():
    # Getting the current date
    # and time
    dt = datetime.datetime.now()

    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    return utc_timestamp


def mock_decorator(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f('', *args, **kwargs)

        return decorated_function

    return decorator


mock.patch('auth.auth.requires_auth', mock_decorator).start()
mock.patch.dict(os.environ, {'EXCITED': 'true'})

from app import create_app


class CrewCase(TestCase):
    """This class represents the trivial test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(True)
        self.client = self.app.test_client
        self.database_name = "crew_test_db"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        db.session.remove()
        db.drop_all()

    def test_get_default(self):
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)

    def test_get_no_actors(self):
        res = self.client().get('/api/actors')

        self.assertEqual(res.status_code, 404)

    def test_get_actors(self):
        new_actor = Actor(name='test', age=12, gender=GenderEnum(1))
        new_actor.save_to_db()

        res = self.client().get('/api/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertGreater(len(data['actors']), 0)

    def test_add_actor(self):
        params = json.dumps({'name': 'test1212', 'age': '12', 'gender': 1})
        res = self.client().post('/api/actors', data=params, headers={'Content-Type': 'application/json'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue('artist' in data)

    def test_add_actor_failed(self):
        params = json.dumps({'name': 'test', 'age': '12', 'gender': 1})
        res = self.client().post('/api/actors', data=params, headers={'Content-Type': 'application/json'})

        self.assertEqual(res.status_code, 422)

    def test_get_no_movies(self):
        res = self.client().get('/api/movies?sortField=release&sortOrder=asc')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['movies']), 0)

    def test_get_movies(self):
        new_movie = Movie(title='test', release=get_utc_timestamp())
        new_movie.save_to_db()

        res = self.client().get('/api/movies?sortField=release&sortOrder=asc')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['movies']), 0)

    def test_add_movie_failed(self):
        params = json.dumps({'title': 'test'})
        res = self.client().post('/api/movies', data=params, headers={'Content-Type': 'application/json'})

        self.assertEqual(res.status_code, 422)

    def test_get_no_crews(self):
        res = self.client().get('/api/crews')

        self.assertEqual(res.status_code, 404)

    def test_get_crews(self):
        new_actor = Actor(name='test', age=12, gender=GenderEnum(1))
        new_actor.save_to_db()
        new_movie = Movie(title='test', release=get_utc_timestamp())
        new_movie.save_to_db()
        new_crew = Crew(actor_id=1, movie_id=1)
        new_crew.save_to_db()

        res = self.client().get('/api/crews')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['crews']), 0)

    def test_add_crew_failed(self):
        params = json.dumps({'artists': None, 'movie_id': 1})
        res = self.client().post('/api/crews', data=params, headers={'Content-Type': 'application/json'})

        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
