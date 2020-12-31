from flask import Flask, Response, request, jsonify
from werkzeug.security import safe_str_cmp
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import pymongo
import Settings.settings
import os
import json

# Setting up for application
app = Flask(__name__)
app.secret_key = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri) 
mongo_db_name = os.getenv("MONGO_DB_NAME")
db = client.get_database(mongo_db_name)  #replace your db name
languages = db.languages  # replace your collection name
userscol = db.users  # replace your collection name


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401



@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    for user in list(userscol.find({"username": username}, {"password", "email"})):
        if user and safe_str_cmp(user.get('password', None), password):
            ret = {'access_token': create_access_token(user.get('email'), expires_delta=False)}
            return jsonify(ret), 200

    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    username = get_jwt_identity()
    return jsonify({'hello': username}), 200

            

@app.route('/users', methods=["GET"])
@jwt_required
def get():
    try:
        data = list(userscol.find())
        return Response(
            response = json.dumps(data,default=str), 
            status=200,
            mimetype="application/json"
            ) 
    except Exception as e:
        return jsonify(e), 404

@app.route('/user/<string:id>', methods=["GET"])
@jwt_required
def getuser(id):
    try:
        data = list(userscol.find({"_id":ObjectId(id)}))
        return Response(
            response = json.dumps(data,default=str), 
            status=200,
            mimetype="application/json"
            ) 
    except Exception as e:
        return jsonify(e), 404
        



if __name__ == "__main__":
    app.run(port=3030, debug=True)