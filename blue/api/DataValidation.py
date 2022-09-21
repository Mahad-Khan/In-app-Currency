class DataValidation:
    """
    performing incoming data validation
    using json schema
    """
    
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
        
