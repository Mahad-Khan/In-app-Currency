#importing libraries
import sys 
import os
import hashlib
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import  create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from email_validator import validate_email
from jsonschema import validate

# adding path for importing moduels
dirname = os.path.dirname(os.path.abspath(__file__))
dirname_list = dirname.split("/")[:-1]
dirname = "/".join(dirname_list)
path = dirname + "/api"
sys.path.append(path)
print(path)

from mongo_connection import MongoConnection
from Dynamo import User, Wallet



    


mod = Blueprint('api',__name__)
api = Api(mod)

connection = MongoConnection()
#getting collections from database
user_collection = connection.get_user_collection()
template_collection = connection.get_template_collection()

#getting schemas for data validation
user_registeration_schema = connection.get_user_schema()
user_login_schema = connection.get_login_schema()
adding_amount_validation = connection.get_adding_amount_validation()
          

class TemplateDetail(Resource):
    @jwt_required()
    def get(self, template_id): #it will get template by ID with authentication
        try:
            current_user_email = get_jwt_identity() # Get the identity of the current user
            template_from_db = template_collection.find_one({'template_id' : int(template_id), "email": current_user_email}, {"_id": 0, "template_id":0})
            if template_from_db:
                return make_response(jsonify({"data": template_from_db}), 200)
            else:
                return make_response(jsonify({'msg': 'template not found'}), 404)    
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
        
    @jwt_required()    
    def delete(self,template_id): #it will delete template by ID with authentication
        try:
            current_user_email = get_jwt_identity() # Get the identity of the current user
            template_from_db = template_collection.find_one({'template_id' : int(template_id), "email": current_user_email}, {"_id": 0, "template_id":0})
            if template_from_db:
                template_from_db = template_collection.delete_one({'template_id' : int(template_id)})
                return make_response(jsonify({"msg": "template deleted"}), 200)
            else:
                return make_response(jsonify({'msg': 'template not found'}), 404)
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
        
    @jwt_required()    
    def put(self,template_id): #it will update template by ID with authentication
        try: 
            data = request.get_json()
            current_user_email = get_jwt_identity() # Get the identity of the current user
            try:
                validate(instance=data, schema=template_schema) # schema validation
            except Exception as e:
                return make_response(jsonify({'msg': 'data validation failure', "reason": str(e)}), 400)
            
            template_from_db = template_collection.find_one({'template_id' : int(template_id), "email": current_user_email}, {"_id": 0, "template_id":0})
            if template_from_db:
                template_collection.update_one({"template_id": int(template_id), "email": str(current_user_email)}, {'$set': data})
                return make_response(jsonify({'msg': 'template updated'}), 200)     
            else:
                return make_response(jsonify({'msg': 'template not found'}), 404)
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
        

class TemplateDetail(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user_email = get_jwt_identity() # Get the identity of the current user
            print(current_user_email)
            balance = wallet_table.get_balance(current_user_email)
            return make_response(jsonify({"balance": balance}), 200)    
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
           
    @jwt_required()        
    def post(self): #it will create template with authentication
        try:
            data = request.get_json()
            current_user_email = get_jwt_identity() # Get the identity of the current user
            print(current_user_email)
            try:
                validate(instance=data, schema=adding_amount_validation) # schema validation
            except Exception as e:
                return make_response(jsonify({'msg': 'Invalid amount', "reason": str(e)}), 400)
            
            
            data['email'] = current_user_email
            # adding data['amount'] in current user balance
            data = wallet_table.update_balance(data)
            return make_response(jsonify({'msg': 'amount added successfully'}), 201)
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
        
class TemplateList(Resource):        
    @jwt_required()        
    def post(self):
        try:
            data = request.get_json()
            current_user_email = get_jwt_identity() # Get the identity of the current user
            print(current_user_email)
            try:
                validate(instance=data, schema=adding_amount_validation) # schema validation
            except Exception as e:
                return make_response(jsonify({'msg': 'Invalid amount', "reason": str(e)}), 400)

            data['email'] = current_user_email
            # adding data['amount'] in current user balance
            data = wallet_table.pay_amount(data)
            if data == "not enough balance":
                return make_response(jsonify({'msg': 'Insufficient funds'}), 400)
            return make_response(jsonify({'msg': 'you have bought premium feature successfully'}), 201)
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
    
 
class Register(Resource):
    def post(self):
        try:
            new_user = request.get_json()
            try:
                validate(instance=new_user, schema=user_registeration_schema) # schema validation
                email = (validate_email(new_user["email"]).email).lower() # email validation and also normalization
            except Exception as e:
                return make_response(jsonify({'msg': 'data validation failure', "reason": str(e)}), 400)
            print("before adding new user")
            user = user_table.get_user(email) # check if user exist
            if user == "user not found":
                new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
                print("adding in dynamo")
                user_table.add_user(new_user)
                return make_response(jsonify({'msg': 'User created successfully'}), 201)
            else:
                return make_response(jsonify({'msg': 'User already exists'}), 409)
            
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
            
            
class Login(Resource):
    def post(self): 
        try:
            login_details = request.get_json() # store the json body request
            try:
                validate(instance=login_details, schema=user_login_schema) # schema validation
                email = (validate_email(login_details["email"]).email).lower() # email validation and also normalization
            except Exception as e:
                return make_response(jsonify({'msg': 'data validation failure', "reason": str(e)}), 400)

            user = user_table.get_user(email)
            if user != "user not found":
                print(user)
                encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
                if encrpted_password == user['password']:
                    access_token = create_access_token(identity=user['email'], fresh=True) # create jwt token
                    refresh_token = create_refresh_token(user['email'])
                    return make_response(jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200)
                else:
                    return make_response(jsonify({'msg': 'Incorrect Password'}), 401)
            else:
                return make_response(jsonify({'msg': 'User not found'}), 404)
        
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
    

api.add_resource(Register,'/register')
api.add_resource(Login,'/login')
