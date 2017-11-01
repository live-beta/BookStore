from flask_restful import fields
# serializer for book fields

BookFormat ={

	"id":fields.Integer,
	"book_name": fields.String,
	"book_isbn": fields.String,
	"stock_count": fields.Integer,
	"book_category": fields.Integer,
}

