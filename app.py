import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db
from auth.auth import requires_auth
from models import GenderEnum, Actor, Movie, Crew
from helpers.pagination import extract_pagination_params, get_per_page, paginated_request
from helpers.string import is_empty_string

RECORDS_PER_PAGE = 10


def create_app(testing=None, test_config=None):
    app = Flask(__name__)
    app.testing = testing
    setup_db(app)
    CORS(app)

    @app.route('/')
    def get_greeting():
        excited = ''
        if 'EXCITED' in os.environ:
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
        gender_values = list(map(lambda value: int(value), request.args.getlist('genders[]')))
        name = request.args.get('name')
        sort_function = None

        pagination['per_page'] = get_per_page(pagination['per_page'], RECORDS_PER_PAGE)

        if 'sort_field' in pagination:
            field = getattr(Actor, pagination['sort_field'])
            sort_function = getattr(field, pagination['sort_order'])

        query = Actor.query

        if sort_function is not None:
            query = query.order_by(sort_function())

        if (gender_values is not None) and (len(gender_values) > 0):
            enum_objs = list(map(lambda value: GenderEnum(value), gender_values))
            query = query.filter(Actor.gender.in_(enum_objs))

        if is_empty_string(name):
            query = query.filter(Actor.name.ilike('%' + name + '%'))

        if (0 != pagination['per_page']) and (0 != pagination['current_page']):
            actors = query.paginate(per_page=pagination['per_page'], page=pagination['current_page'])

            if 0 == len(actors.items):
                abort(404)

            return jsonify({
                'actors': list(map(lambda actor: actor.format(), actors.items)),
                'totalCount': actors.total,
                'currentPage': pagination['current_page'],
                'perPage': pagination['per_page'],
                'filters': {'genders': gender_values},
                'sortField': pagination['sort_field'] if 'sort_field' in pagination else '',
                'sortOrder': pagination['sort_order'] if 'sort_order' in pagination else '',
                'success': True
            })
        else:
            actors = query.all()

            if 0 == len(actors):
                abort(404)

            return jsonify({
                'actors': list(map(lambda actor: actor.format(), actors)),
            })

    @app.route('/api/actors', methods=['POST'])
    @requires_auth('create:actor')
    def create_actors(payload):
        print('New actor: ')
        print(request.json)
        name = request.json['name']
        age = int(request.json['age']) if 'age' in request.json else 0

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

    @app.route("/api/actors/<int:actor_id>", methods=['PATCH'])
    @requires_auth('edit:actor')
    def update_actor(payload, actor_id):
        try:
            actor = Actor.query.filter_by(id=actor_id).first()
            if 'name' in request.json:
                actor.name = request.json['name']
            if 'age' in request.json:
                actor.age = int(request.json['age'])
            if 'gender' in request.json:
                actor.gender = GenderEnum(request.json['gender'])
            actor.update()

            return jsonify({
                'success': True,
                'artist': actor.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/api/movies')
    @requires_auth('view:movies')
    @paginated_request
    def show_movies(pagination, payload):
        if 'get_all' in pagination:
            movie_list = Movie.query.order_by(Movie.release.desc()).all()
            return jsonify({
                'movies': list(map(lambda movie: movie.format(), movie_list))
            })
        else:
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
                'perPage': pagination['per_page'],
                'success': True
            })

    @app.route('/api/movies', methods=['POST'])
    @requires_auth('create:movie')
    def create_movies(payload):
        print('New movie: ')
        print(request.json)
        title = request.json['title']
        release = int(request.json['releaseDate']) if 'releaseDate' in request.json else 0

        if (title is None) or ('' == title) or (len(title) < 5):
            print('Invalid title provided')
            abort(422)

        if (release is None) or (0 == release):
            print('Invalid release provided')
            abort(422)

        new_movie = Movie(title=title, release=release)
        result = new_movie.save_to_db()

        return jsonify({
            'success': result,
            'movie': new_movie.format(),
        })

    @app.route("/api/movies/<int:movie_id>", methods=['PATCH'])
    @requires_auth('edit:movie')
    def update_movie(payload, movie_id):
        try:
            movie = Movie.query.filter_by(id=movie_id).first()
            if 'title' in request.json:
                movie.title = request.json['title']
            if 'releaseDate' in request.json:
                movie.release = int(request.json['releaseDate'])

            movie.update()

            return jsonify({
                'success': True,
                'movie': movie.format()
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route("/api/movies/<int:movie_id>", methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(payload, movie_id):
        movie = Movie.query.filter_by(id=movie_id).first()
        try:
            movie.delete_from_db()
            return jsonify({'success': True})
        except:
            abort(500)

    @app.route('/api/crews', methods=['GET'])
    @requires_auth('update:crew')
    def get_crew_list(payload):
        crew_list = Crew.query.all()

        if len(crew_list) == 0:
            abort(404)

        try:
            return jsonify({
                'crews': list(map(lambda crew: crew.format(), crew_list)),
                'success': True,
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/api/crews', methods=['POST'])
    @requires_auth('update:crew')
    def assign_crew(payload):
        print('New crew: ')
        movie_id = request.json['movie_id']
        artist_list = request.json['artists']

        if movie_id is None:
            print('No movie found')
            abort(422)

        records = Crew.query.filter(Crew.movie_id == request.json['movie_id']).all()

        if len(records) > 0:
            for record in records:
                record.delete_from_db()

        if artist_list is not None:
            try:
                for val in artist_list:
                    new_crew = Crew(actor_id=val, movie_id=movie_id)
                    new_crew.save_to_db()

                return jsonify({'success': True, 'result': request.json})
            except Exception as e:
                print(e)
                abort(422)
        else:
            print('No artist list found')
            abort(422)

    # Error Handling
    '''
    Example error handling for unprocessable entity
    '''

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    '''
    Handles no resource found error
    '''

    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Provided resource cannot be found"
        }), 404

    '''
    Handles unauthorized access error
    '''

    @app.errorhandler(401)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "Unauthorized access"
        }), 401

    @app.errorhandler(403)
    def no_permission_granted(error):
        return jsonify({
            "success": False,
            "error": 403,
            "message": "No permission granted"
        }), 403

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
