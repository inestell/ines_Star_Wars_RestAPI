"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)




# Users endpoints

@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    all_people = list(map(lambda x: x.serialize(), users))

    return jsonify(all_people), 200

@app.route('/user', methods=['POST'])
def create_user():
    
    request_body_user = request.get_json()
    user1 = User(email=request_body_user["email"], password=request_body_user["password"])
    db.session.add(user1)
    db.session.commit()

    return jsonify(request_body_user), 200




# Characters endpoints

@app.route('/characters', methods=['POST'])
def create_character():
    request_body_user = request.get_json()
    character1 = Characters(
        name=request_body_user["name"], 
        height=request_body_user["height"],
        mass=request_body_user["mass"],
        hair_color=request_body_user["hair_color"],
        skin_color=request_body_user["skin_color"],
        eye_color=request_body_user["eye_color"],
        birth_year=request_body_user["birth_year"],
        gender=request_body_user["gender"]
        )
    db.session.add(character1)
    db.session.commit()

    return "Success", 200


@app.route('/characters', methods=['GET'])
def handle_character():
    characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), characters))

    return jsonify(all_characters), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Characters.query.get(character_id)
    one_character = character.serialize()

    return jsonify(one_character), 200


@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Characters.query.get(character_id)
    db.session.delete(character)
    db.session.commit()

    return "Success", 200





# Planets endpoints

@app.route('/planets', methods=['POST'])
def create_planet():
    request_body_user = request.get_json()
    planet1 = Planets(
        name=request_body_user["name"], 
        rotation_period=request_body_user["rotation_period"],
        orbital_period=request_body_user["orbital_period"],
        diameter=request_body_user["diameter"],
        climate=request_body_user["climate"],
        terrain=request_body_user["terrain"],
        )
    db.session.add(planet1)
    db.session.commit()

    return "Success", 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))

    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    one_planet = planet.serialize()

    return jsonify(one_planet), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    db.session.delete(planet)
    db.session.commit()

    return "Success", 200



# Favorites endpoints

@app.route('/favorites/user/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)

    favorite_planets = (
        db.session.query(Favorites, Planets)
        .join(Planets)
        .filter(Favorites.user_id == user_id)
        .all()
    )

    list_favorite_planets = list(map(lambda x: x.serialize(), favorite_planets))

    return jsonify(list_favorite_planets), 200


@app.route('/favorites/user/<int:user_id>/planets/<int:planet_id>', methods=['POST'])
def create_favorite_planet(user_id, planet_id):
    
    new_favorite_planet = Favorites(user_id = user_id, favorite_planet = planet_id)

    db.session.add(new_favorite_planet)
    db.session.commit()
    
    return "Success", 200




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
