from config import Config
from flask import Flask
from flask_cors import CORS
import sqlalchemy as db
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask.json import JSONEncoder
from datetime import date

# -*- coding: utf-8 -*-


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


# insert db credential here
# url = 'mysql+mysqlconnector://dbmasteruser:>0&b0z02rsN-~M[Gny3YM=YBzkcUgMM7@ls-912c29a641fcdb7c731eec956e4b36c8c1a643aa.c6vcr3vpaybq.ap-northeast-1.rds.amazonaws.com/PaymentGateway'
url = 'mysql+mysqlconnector://root:@127.0.0.1/ppc_payment'
Base = declarative_base()
engine = db.create_engine(url, echo=True, pool_size=100, max_overflow=20)
session = flask_scoped_session(sessionmaker(bind=engine))
app = Flask(__name__)
app.secret_key = "key"
app.config.from_object(Config)
app.json_encoder = CustomJSONEncoder
cors = CORS(app)
key = app.config['SECRET_KEY']
jwt = JWTManager(app)
mail = Mail(app)
login_manager = LoginManager()
db = SQLAlchemy(app)
db.init_app(app)

from app.routers.all_router import *
from app.routers.user_router import *

app.register_blueprint(allroute_blueprint)
app.register_blueprint(users_blueprint)
