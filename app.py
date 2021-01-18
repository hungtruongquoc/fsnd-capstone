import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db
from auth.auth import requires_auth
from models import GenderEnum, Actor, Movie
from helpers.pagination import extract_pagination_params, get_per_page, paginated_request

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

    @app.route('/api/actors')
    @requires_auth('view:actors')
    @paginated_request
    def show_actors(pagination, payload):
        sort_field = request.args.get('sortField')
        sort_order = request.args.get('sortOrder')
        status_values = list(map(lambda value: int(value), request.args.getlist('status[]')))
        name = request.args.get('name')

        pagination['per_page'] = get_per_page(pagination['per_page'], RECORDS_PER_PAGE)

        field = getattr(Actor, sort_field)
        sort_function = getattr(field, sort_order)

        query = Actor.query.order_by(sort_function())

        if (status_values is not None) and (len(status_values) > 0):
            print(status_values)
            enum_objs = list(map(lambda value: GenderEnum(value), status_values))
            query = query.filter(Actor.gender.in_(enum_objs))

        if (name is not None) and ('' != name) and (' ' != name):
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

    @app.route('/api/movies')
    @requires_auth('view:movies')
    @paginated_request
    def show_movies(pagination, payload):
        pagination['per_page'] = get_per_page(pagination['per_page'], RECORDS_PER_PAGE)
        query = Movie.query
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

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
