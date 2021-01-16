import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import setup_db
from auth.auth import requires_auth


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
    def show_actors(payload):
        return jsonify([])

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
