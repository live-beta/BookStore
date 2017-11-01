
from app import db
from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

# Class experimenting with users and books

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    # employee_code = db.Column(db.String(255),unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hformat = db.Column(db.String(255), nullable=False)
    # bucketlist = db.relationship('Bucketlist', backref='user', lazy='dynamic',
    #                              cascade='all,delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is hashed and cannot be read')

    @password.setter
    def password(self, password):
        self.password_hformat = generate_password_hash(password)

    def auth_password(self, password):
        return check_password_hash(self.password_hformat, password)

    def confirmation_token(self, expiration=40000):
        serial = Serializer(current_app.config['SECRET_KEY'], expiration)
        return serial.dumps({'id': self.id})

    @staticmethod
    def comfirm_token(token):
        serial = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = serial.loads(token)
        except:
            """ Token is not valid"""
            return False
        return data["id"]

# Book model definition

class Books(db.Model):
    __tablename__ ='books'
    id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(255), nullable=False)
    book_idbm = db.Column(db.String(255), nullable=False)
    stock_count = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)




