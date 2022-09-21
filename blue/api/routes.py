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
from boto3 import resource
import config

# getting access keys from config file for aws dynamo db auth
AWS_ACCESS_KEY_ID     = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
REGION_NAME           = config.REGION_NAME

# Get the service resource.
dynamodb = resource(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)

# checking if tables are created
user_table = User(dynamodb)
if user_table.exists('users'):
    print('User table found')
else:
    print('User table not found')
        
wallet_table = Wallet(dynamodb)
if wallet_table.exists('wallet'):
    print('Wallet table found')
else:
    print('Wallet table not found')

    

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
          

class AddCurrency(Resource):
    """
    It supports adding amount into the wallet 
    also getting balance from the wallet
    """
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
        
class PayCurrency(Resource):
    """
    It is reponsible to pay amount
    from the wallet to buy premium features
    """        
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
            data = wallet_table.pay_amount(data)
            if data == "not enough balance":
                return make_response(jsonify({'msg': 'Insufficient funds'}), 400)
            #assumption: Here, we have paid the amount for premium feature
            return make_response(jsonify({'msg': 'you have bought premium feature successfully'}), 201)
        except Exception as e:
            return make_response(jsonify({'msg': 'faliure', "reason": str(e)}), 500)
    
 
class Register(Resource):
    """
    User registration with first_name, last_name
    email, and password
    """
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
    """
    login the user and return jwt token
    """
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
    
    
api.add_resource(PayCurrency,'/pay')
api.add_resource(AddCurrency,'/currency')
api.add_resource(Register,'/register')
api.add_resource(Login,'/login')