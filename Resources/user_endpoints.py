from flask.views import MethodView
from flask_smorest import abort, Blueprint #type:ignore
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256 #type:ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, create_refresh_token # type: ignore
from blocklist import BLOCKLIST 

from database import db
from Models import UserModel, VideoModel
from schemas import UserSchema, UserLoginSchema, VideoDetailsSchema


blp = Blueprint("Users", "users", description = "Operations on User")

@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        is_admin= False
        if UserModel.query.filter_by(user_email=user_data["user_email"]).first():
            abort(409, message="User with that email already exists.")
        
        if user_data["user_email"].find("vdojar.com") != -1:
            is_admin= True

        user = UserModel(
            user_first_name=user_data["user_first_name"],
            user_last_name=user_data["user_last_name"],
            user_email=user_data["user_email"],
            user_password=pbkdf2_sha256.hash(user_data["user_password"]),
            is_admin = is_admin
        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while registering the user.")

        return {"message": "User registered successfully"}, 201


@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.user_email == user_data["user_email"]).first()

        if user and pbkdf2_sha256.verify(user_data["user_password"], user.user_password):
            access_token = create_access_token(
                identity=str(user.user_id), 
                fresh=True,
                additional_claims={"is_admin": user.is_admin}
            )
            return {"message": "Login successful", "access_token": access_token}, 200
        
        abort(401, message="Invalid credentials")


@blp.route("/user/<int:user_id>")
class User(MethodView):

    @jwt_required()
    @blp.response(200)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        videos = VideoModel.query.filter_by(user_id=user_id).all()

        return {
            "user": {
                "user_id": user.user_id,
                "user_first_name": user.user_first_name,
                "user_last_name": user.user_last_name,
                "user_email": user.user_email,
                "is_admin" : user.is_admin
            },
            "videos": [
                {
                    "video_id": video.video_id,
                    "video_filename": video.video_filename,
                    "video_title": video.video_title,
                    "video_description": video.video_description,
                    "video_genre": video.video_genre.split(",") if video.video_genre else [],
                    "thumbnails": video.thumbnail.to_dict()  # Get all related thumbnails
                }
                for video in videos
            ]
        }


@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        #  we can get the access token by both the way
        # jti = get_jwt().get("jti") 
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": "Successfully Logout."}