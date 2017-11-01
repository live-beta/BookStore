from flask_httpauth import HTTPTokenAuth
from flask import jsonify, g

from app.stock.models import User

# Setting up the Authorization header with a token profix

token_auth = HTTPTokenAuth("Bearer")

# Verifying the user security validity

@token_auth.verify_token
def verify_token(token):
    """ Verifies the user authentication token"""
    user_active_id = User.comfirm_token(token)
    if user_active_id:
        g.user = User.query.filter_by(id=user_active_id).first()
        return True
    return False

@token_auth.error_handler
def auth_error():
    """ Returns messege from unauthorised Access """
    return jsonify({"messege":"Access not Allowed, Invalid token"}), 401
