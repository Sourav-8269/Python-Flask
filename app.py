from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User(username = {self.username}, email = {self.email})"

user_args = reqparse.RequestParser()
user_args.add_argument('username', type=str, help='Username is required', required=True)
user_args.add_argument('email', type=str, help='Email is required', required=True)

userFields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String
}

class Users (Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args['username'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        return user, 201
    
class User (Resource):
    @marshal_with(userFields)
    def get(self, user_id):
        result = UserModel.query.filter_by(id=user_id).first()
        if not result:
            abort(404, message="User {} doesn't exist".format(user_id))
        return result
    
    @marshal_with(userFields)
    def patch(self, user_id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User {} doesn't exist".format(user_id))
        user.username = args['username']
        user.email = args['email']
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self, user_id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User {} doesn't exist".format(user_id))
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users
    
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:user_id>')

@app.route('/')
def home():
    return '<h1>Home</h1>'

if __name__ == '__main__':
    app.run(debug=True)