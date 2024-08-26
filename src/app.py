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
from models import db, User, People, Planet,FavoritePeople,FavoritePlanet
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
@app.route('/people', methods=['GET'])
def get_people_all():
    peoples= People.query.all()
    serialized_peoples = [people.serialize() for people in peoples]
    return jsonify({"peoples": serialized_peoples})

@app.route('/peoples/<int:people_id>', methods=['GET'])
def get_peoples(people_id):
    try:
        peoples = People.query.get(people_id)
        if peoples is None:
            return jsonify({'error': "Person no fund!"}), 400
        return jsonify({"person": peoples.serialize()}), 200
    
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@app.route('/planets', methods=['GET'])
def get_planets_all():
    planets= Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify({"planets": serialized_planets})

@app.route('/planets/<int:plnet_id>', methods=['GET'])
def get_planets(planet_id):
    try:
        planets = Planet.query.get(planet_id)
        if planets is None:
            return jsonify({'error': "Planet no fund!"}), 400
        return jsonify({"planet": planets.serialize()}), 200 
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500
    
@app.route('/users', methods=['GET'])
def get_users_all():
    users= User.query.all()
    serialized_users = [user.serialize() for user in users]
    return jsonify({"users": serialized_users})

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
  
    user_id = request.args.get('user_id') 
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorites_planets = FavoritePlanet.query.filter_by(user_id=user_id).all()
    favorites_people = FavoritePeople.query.filter_by(user_id=user_id).all()
    
    serialized_favorites_planets = [fp.serialize() for fp in favorites_planets]
    serialized_favorites_people = [fp.serialize() for fp in favorites_people]
    
    return jsonify({
        'favorites_planets': serialized_favorites_planets,
        'favorites_people': serialized_favorites_people
    })

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')  
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    existing_favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({'error': "Favorite already exists!"}), 400

    favorite = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify(favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.args.get('user_id') 
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    existing_favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({'error': "Favorite already exists!"}), 400

    favorite = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify(favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id') 
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({'error': "Favorite not found!"}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': "Favorite deleted!"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.args.get('user_id')  
    if not user_id:
        return jsonify({'error': "User ID is required!"}), 400
    
    favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({'error': "Favorite not found!"}), 404
    
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': "Favorite deleted!"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
