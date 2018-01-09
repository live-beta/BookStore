from flask_restful import fields
# serializer for book fields

BookFormat ={

	"id":fields.Integer,
	"book_name": fields.String,
	"book_isbn": fields.String,
	"book_category": fields.String,
	"subtitle" :  fields.String,
    # "authors" : fields.String,
    "description" : fields.String,
    "publishedDate" :  fields.String,
    # "industryIdentifiers" :  fields.String

}

