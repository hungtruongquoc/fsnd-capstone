import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db
from auth.auth import requires_auth
from models import GenderEnum, Actor, Movie
from helpers.pagination import extract_pagination_params, get_per_page, paginated_request
from helpers.string import is_empty_string

RECORDS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def get_greeting():
        excited = os.environ['EXCITED']
        greeting = "Hello"
        if excited == 'true':
            greeting = greeting + "!!!!!"
        return greeting

    @app.route('/coolkids')
    def be_cool():
        return "Be cool, man, be coooool! You're almost a FSND grad!"

    @app.route('/api/stats')
    @requires_auth('view:actors')
    def show_stats(payload):
        return jsonify({'movies': Movie.query.count(), 'actors': Actor.query.count()})

    @app.route('/api/actors')
    @requires_auth('view:actors')
    @paginated_request
    def show_actors(pagination, payload):
        status_values = list(map(lambda value: int(value), request.args.getlist('status[]')))
        name = request.args.get('name')

        pagination['per_page'] = get_per_page(pagination['per_page'], RECORDS_PER_PAGE)
        field = getattr(Actor, pagination['sort_field'])
        sort_function = getattr(field, pagination['sort_order'])

        query = Actor.query

        if sort_function is not None:
            query = query.order_by(sort_function())

        if (status_values is not None) and (len(status_values) > 0):
            print(status_values)
            enum_objs = list(map(lambda value: GenderEnum(value), status_values))
            query = query.filter(Actor.gender.in_(enum_objs))

        if is_empty_string(name):
            query = query.filter(Actor.name.ilike('%' + name + '%'))

        actors = query.paginate(per_page=pagination['per_page'], page=pagination['current_page'])

        if len(actors.items) == 0:
            abort(404)

        return jsonify({
            'actors': list(map(lambda actor: actor.format(), actors.items)),
            'totalCount': actors.total,
            'currentPage': pagination['current_page'],
            'perPage': pagination['per_page']
        })

    @app.route('/api/actors', methods=['POST'])
    @requires_auth('create:actor')
    def create_actors(payload):
        print('New actor: ')
        print(request.json)
        name = request.json['name']
        age = request.json['age']

        if (name is None) or ('' == name) or (len(name) < 5):
            print('Invalid name provided')
            abort(422)

        if (age is None) or (3 > age) or (99 < age):
            print('Invalid age provided')
            abort(422)

        try:
            gender = GenderEnum(request.json['gender'])
            new_artist = Actor(name=name, age=age, gender=gender)
            result = new_artist.save_to_db()

            return jsonify({
                'success': result,
                'artist': new_artist.format(),
            })
        except ValueError:
            print('Invalid gender provided')
            abort(422)

    @app.route("/api/actors/<int:actor_id>", methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(payload, actor_id):
        actor = Actor.query.filter_by(id=actor_id).first()
        try:
            actor.delete_from_db()
            return jsonify({'success': True})
        except:
            abort(500)

    @app.route('/api/movies')
    @requires_auth('view:movies')
    @paginated_request
    def show_movies(pagination, payload):
        pagination['per_page'] = get_per_page(pagination['per_page'], RECORDS_PER_PAGE)
        title = request.args.get('title')

        field = getattr(Movie, pagination['sort_field'])
        sort_function = getattr(field, pagination['sort_order'])

        query = Movie.query

        if sort_function is not None:
            query = query.order_by(sort_function())

        if is_empty_string(title):
            query = query.filter(Movie.title.ilike('%' + title + '%'))

        movies = query.paginate(per_page=pagination['per_page'], page=pagination['current_page'])
        return jsonify({
            'movies': list(map(lambda movie: movie.format(), movies.items)),
            'totalCount': movies.total,
            'currentPage': pagination['current_page'],
            'perPage': pagination['per_page']
        })

    @app.route('/api/movies', methods=['POST'])
    @requires_auth('create:movie')
    def create_movies(payload):
        print('New movie: ')
        print(request.json)
        title = request.json['title']
        release = int(request.json['releaseDate'])

        if (title is None) or ('' == title) or (len(title) < 5):
            print('Invalid title provided')
            abort(422)

        if release is None:
            print('Invalid release provided')
            abort(422)

        new_movie = Movie(title=title, release=release)
        result = new_movie.save_to_db()

        return jsonify({
            'success': result,
            'movie': new_movie.format(),
        })

    @app.route("/api/movies/<int:movie_id>", methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(payload, movie_id):
        movie = Movie.query.filter_by(id=movie_id).first()
        try:
            movie.delete_from_db()
            return jsonify({'success': True})
        except:
            abort(500)

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
