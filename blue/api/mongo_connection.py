
from pymongo import MongoClient

class MongoConnection:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://User1:User1@cluster0.qba5b05.mongodb.net/?retryWrites=true&w=majority") # your connection string
        self.db = self.client["mydatabase"]
        self.template_collection = self.db["template_collection"]
        self.user_collection = self.db["user_collection"]
    
    def get_template_collection(self):
        return self.template_collection
    
    def get_user_collection(self):
        return self.user_collection
    
    def get_user_schema(self):
        schema = {
                "type": "object",
                "required": ["first_name","last_name", "email", "password"],
                "properties": {
                    "first_name": {"type": "string", "pattern": "[a-z0-9]{1,15}"},
                    "last_name": {"type": "string", "pattern": "[a-z0-9]{1,15}"},
                    "email": {"type": "string"},
                    "password": {"type": "string", "pattern": "[a-zA-Z0-9_.-@#$%]{4,15}"}    
                },
                }
        return schema
    
    def get_login_schema(self):
        schema = {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                    
                },
                }
        return schema
    
    def get_adding_amount_validation(self):
        schema = {
                "type": "object",
                "required": ["amount"],
                "properties": {
                    "amount": {"type": "number", "exclusiveMinimum": 0}
                },
                }
        return schema
        
