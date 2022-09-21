import datetime
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'mahad@123'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
CORS(app)


from blue.api.routes import mod

app.register_blueprint(mod,url_prefix = '/api')
