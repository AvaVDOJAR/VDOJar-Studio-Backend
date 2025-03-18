import os
from flask import Flask, jsonify
from flask_smorest import Api #type:ignore
from flask_cors import CORS #type:ignore
from database import db
import cloudinary #type:ignore

from flask_jwt_extended import JWTManager  # type: ignore
from blocklist import BLOCKLIST

from Resources.video_endpoints import blp as VideoBlueprint
from Resources.thumbnail_endpoints import blp as ThumbnailBlueprint
from Resources.user_endpoints import blp as UserBlueprint


# importing the api related from loudnary api
from apis import cloud_name, api_key, api_secret, jwt_secret_key


def create_app(db_url = None):
    app = Flask(__name__)
    # Allow any request from 'http://localhost:port' and any headers
    CORS(app, 

         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],  # Allow necessary headers
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Allow all necessary methods
    )

    cloudinary.config( 
        cloud_name = cloud_name, 
        api_key = api_key, 
        api_secret = api_secret, # Click 'View API Keys' above to copy your API secret
        secure=True
    )

    app.config["PROPAGATE_EXCEPTION"] = True

    # flask_smorest configurations
    app.config["API_TITLE"] = "Data Storing Backend"
    app.config["API_VERSION"] = "v1"
    # here OPENAPI_VERSION it is a standard default
    app.config["OPENAPI_VERSION"] = "3.0.3"

    # this is for url prefix -> url start with
    app.config["OPENAPI_URL_PREFIX"] = "/"

    # This is for UI of the website
    app.config["OPENAPI_SWAGGER_UI_PATH"] ="/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")

    # this for sqlalchemy track modifications, which basically we don't need it slows down the sqlalchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initializes the flask sqlalchemy extension giving it our flask app
    db.init_app(app)

    # this is for the connect the flask smorest extension with Flask app
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = jwt_secret_key

    # Set access token expiration (e.g., 15 minutes)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 1800  # 1800 seconds = 30 minutes
    jwt = JWTManager(app)


    # this call back function checks the payloads token is present in the blocklist or not
    # if this comes out to be true then the user get logged out 
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    # adding the additional claims for admin only 
    """
    How to identify the admin that code is I am writing here

    """


    # handling the error message given by jwt
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message" : "The token has expired.", "error": "token_expired" 
            }), 401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify({
                "message" : "Signature verification failed.", "error": "invalid_token" 
            }), 401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({
                "description" : "Request does not contain an access token.", "error": "authorization_required" 
            }), 401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify({
                "description" : "The token is not fresh.", "error": "fresh_token_required" 
            }), 401
        )


    with app.app_context():
        db.create_all() # if the tables are already exist it don't create it

    api.register_blueprint(VideoBlueprint)
    api.register_blueprint(ThumbnailBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

