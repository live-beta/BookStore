from flask_restful import fields

# conversion of model attributes to fields

# Conversion of user and book attributes into fields

BookFormat ={
	"id":fields.Integer,
	"book_name": fields.String,
	"book_idbm": fields.String,
	"stock_count": fields.Integer
}

# Itemformat = {"id": fields.Integer,
#               "name": fields.String,
#               "date_created": fields.DateTime(dt_format = "rfc822"),
#               "date_modified": fields.DateTime(dt_format="rfc822"),
#               "done": fields.Boolean(attribute="status")

# }

# bucketlistformat ={"id": fields.Integer,
#                     "name": fields.String,
#                     "items":fields.List(fields.Nested(Itemformat)),
#                     "date_created": fields.DateTime(),
#                     "date_modified": fields.DateTime(),
#                     "creator": fields.String(attribute="user.username")}
