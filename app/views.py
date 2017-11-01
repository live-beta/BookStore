#! /usr/bin/env python
import re
from flask_restful import abort, inputs, Resource, reqparse, marshal_with
from flask import abort, jsonify, request
from app import db, expiry_time
from app.models import User, Books
from app.user_auth import token_auth, g
from app.utils import save, delete, is_not_empty
from app.serializer import BookFormat


class LoginUser(Resource):
    """ User login and token production"""

    def __init__(self):
        # Input validation by request perser

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True,
                                   help="Enter Username")
        self.reqparse.add_argument('password', type=str, required=True,
                                   help="Enter the password")

        super(LoginUser, self).__init__()

    def post(self):
        """Processing User deatils and returning token"""

        args = self.reqparse.parse_args()
        # Assigning the user varble inoformation

        username, password = args["username"], args["password"]
        user = User.query.filter_by(username=username).first()
        if not user or not user.auth_password(password):
            return {"message": "Could not log you in, Check credentials"} 
        # returnign token as as dtring from decode function
        token = user.confirmation_token(expiry_time)
        return {"token": token.decode("ascii")}, 200


class RegisterUser(Resource):

    """Class for registering new users """

    def __init__(self):
        # validating inputs for
        self.reqparse = reqparse.RequestParser()
        # persing the unsername
        self.reqparse.add_argument("username", type=str, required=True,
                                   help="Enter a user name")
        # Parsing the user password
        self.reqparse.add_argument("password", type=str, required=True,
                                   help="Enter a password")
        # persing the user email
        self.reqparse.add_argument("email", type=str, required=True,
                                   help="Enter an email")

        super(RegisterUser, self).__init__()

    def post(self):
        """ Function to create a new user"""
        args = self.reqparse.parse_args()
        username, password, email = (args["username"].lower(), args["password"],
                                     args["email"])
        # Validating the user input using regular expressions
        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            return{"message": ("only numbers, letters, '-','-','.' allowed"
                               "in username entry")}, 400
        # Validating email inputs with regular expressions
        if not re.match("\S+[@]\S+[.]\S", email):
            return {"message": "Enter a valid email"}, 400

        # Password validation by size

        if len(password) < 6:
            return{"message": "password must be at least 6 characters"}, 400

        user_info = User.query.filter_by(username=username).first()
        # Condition to check itf the username entered is available for a new
        # user

        if user_info is not None:
            return{"message": "The username you have entered is not available,\
                    try a different one"}, 403
        user = User(username=username, email=email, password=password)
        save(user)
        # Return a message id the user has been successfully added to the
        # system

        msg = "You have been successfully added as " + user.username
        return {"message": msg}, 201


class BookAction(Resource):
    """ Class for all the operations of bucketlist """
    # Check for a valid tocken before executing the function in this class
    decorators = [token_auth.login_required]

    def __init__(self):
        """Request parser to validate input """
        self.reqparse = reqparse.RequestParser()
        super(BookAction, self).__init__()

    def post(self, id=None):
        """ Function to make a new bucketlist"""
        if id:
            abort(400, "This is a bad request, try again")
        self.reqparse.add_argument("book_name", type=str, required=True,
                                   help="Book Name Required")
        self.reqparse.add_argument("book_idbm", type=str, required=True,
                                   help="Book IDBM Required")
        self.reqparse.add_argument("stock_count", type=int, required=True,
                                   help="Book Name Required")
        args = self.reqparse.parse_args()
        book_name = args["book_name"]
        book_idbm = args["book_idbm"]
        stock_count = args["stock_count"]

        # Validating the user inputs
        if not is_not_empty(book_name):
            return {"message": "No blank book names allowed"}, 400
        
        if book_name.isspace():
            return{"message": "The name you have entered is not relevant"}, 400

        # creating and saving an instance of a bucket
        book_instance = Books(book_name=book_name, book_idbm=book_idbm, stock_count=stock_count, user_id=g.user.id)
        save(book_instance)
        msg = (book_instance.book_name + "of ID" + str(book_instance.id) + " Has been \
                saved successfully")
        return {"message": msg}, 201

    @marshal_with(BookFormat)
    def get(self, id=None):
        """ API Get method call for  books"""
        search = request.args.get("q") or None
        page = request.args.get("page") or 1
        limit = request.args.get("limit") or 20
        if id:
            book_obj = Books.query.filter_by(id=id).first()
            if not book_obj or (book_obj.user_id != g.user.id):
                abort(404, "The requested bucketlist is not found")
            return book_obj, 200
        if search:
            book_search_results = Books.query.filter(Books.name.ilike(
                "%" + search + "%")).filter_by(user_id=g.user.id).paginate(int(page),
                                                                           int(limit),
                                                                           False)

            if len(book_search_results.items) == 0:
                abort(404, "The requested book seems to be missing")
            else:
                book_result = [book_result for book_result in
                              book_search_results.items]
                return book_result, 200

        if page or limit:
            book_collection = Books.query.filter_by(user_id=g.user.id).paginate(int(page),
                                                                                           int(
                                                                                               limit),
                                                                                           False)
            book_display = [
                book_disp for book_disp in book_collection.items]
            return bucket_display, 200

    def put(self, book_idbm=None):
        """ Altering Book content"""

        if not book_idbm:
            return {"message": "Bad request"}, 400
        self.reqparse.add_argument("book_idbm", type=str, required=True,
                                   help="Book IDBM is required")

        args = self.reqparse.parse_args()
        book_idbm = args["book_idbm"]

        # Validation of user inputs bucketlist changes
        if not is_not_empty(book_idbm):
            return{"message": "No blank fields allowed"}, 400
        if book_idbm.isspace():
            return {"message": "The IDBM entered is invalid "}, 400
        book_info = Books.query.filter_by(book_idbm=book_idbm).first()
        if not book_info or (book_info.user_id != g.user.id):
            abort(404, "Book is not found")
        book_info.stock_count = stock_count + 1
        save(book_info)
        msg = ("Book ID: " + str(book_info.id) + "Is Updated")
        return {"message": msg}, 200

    def delete(self, book_idbm=None):
        """Deleting a bucketlist"""
        if not book_idbm:
            abort(400, "bad request")
        book_del = Books.query.filter_by(book_idbm=book_idbm).first()
        if not book_del or (book_del.user_id != g.user.id):
            abort(404, "The book is not in the system")
        delete(book_del)
        msg = ("book : " + book_del.name + " Deleted successfully")
        return {"message": msg}, 200


# class ItemAction(Resource):
#     """ Handles CRUD operations for items in bucketlist"""
#     decorators = [token_auth.login_required]

#     def __init__(self):
#         """ add request parser to validate inputs"""
#         self.reqparse = reqparse.RequestParser()
#         super(ItemAction, self).__init__()

#     def post(self, id=None):
#         """ make a new Item """
#         self.reqparse.add_argument("name", type=str, required=True,
#                                    help="Item name required")
#         args = self.reqparse.parse_args()
#         name = args["name"]
#         # validation of user inputs
#         if not is_not_empty(name):
#             return {"message": "no blank fields allowed"}, 400
#         if name.isspace():
#             return {"message": "name is invalid"}, 400
#         bucketlist = Bucketlist.query.filter_by(id=id).first()
#         if not bucketlist or (bucketlist.user_id != g.user.id):
#             abort(404, "bucketlist not found, confirm the id")
#         item = Item(name=name, bucket_id=id)
#         save(item)
#         msg = ("item has been added to the bucketlist")
#         return {"message": msg}, 201

#     def put(self, id=None, Item_id=None):
#         """ modify an item given name and status or combination of both"""
#         self.reqparse.add_argument("name", type=str, help="item name required")
#         self.reqparse.add_argument("status", type=inputs.boolean,
#                                    location="json",
#                                    help="status required as true or false")
#         args = self.reqparse.parse_args()
#         name, status = args["name"], args["status"]
#         if not id or not Item_id:
#             abort(400, "bad request")
#         if name is None and status is None:
#             abort(400, "provide at least one parameter to change")

#         bucket = Bucketlist.query.filter_by(id=id).first()
#         item = Item.query.filter_by(id=Item_id).first()
#         if not bucket or (bucket.user_id != g.user.id) or not item:
#             abort(404, "Item not found, confirm bucketlist and item id")

#         if status is True or status is False:
#             item.status = status
#         if name is not None:
#             if not is_not_empty(name):
#                 return {"message": "name can't be blank"}, 400
#             if name.isspace():
#                 return {"message": "name is invalid"}, 400
#             item.name = name

#         return {"message": "item has been updated"}, 200

#     def delete(self, id=None, Item_id=None):
#         """ delete the item """
#         bucket = Bucketlist.query.filter_by(id=id).first()
#         item = Item.query.filter_by(id=Item_id).first()
#         if not bucket or (bucket.user_id != g.user.id) or not item:
#             abort(404, "item not found, confirm bucketlist and item id")
#         delete(item)

#         return {"message": "item has been deleted successfully"}, 200
