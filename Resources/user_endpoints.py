from flask.views import MethodView
from flask_smorest import abort, Blueprint  # type:ignore
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import pbkdf2_sha256  # type:ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt , get_jwt_identity # type: ignore
from blocklist import BLOCKLIST

from database import db
from Models import UserModel, VideoModel
from schemas import UserSchema, UserLoginSchema, VideoDetailsSchema

from flask_mail import Message  # type:ignore
from extensions import mail
from itsdangerous import URLSafeTimedSerializer,BadSignature, SignatureExpired
from flask import current_app, url_for

from Resources.verification_msg import html_msg

from apis import jwt_secret_key

blp = Blueprint("Users", "users", description="Operations on User")

# ============================
# ✅ Email Verification Helper
# ============================

def send_verification_email(email):
    serializer = URLSafeTimedSerializer(jwt_secret_key)
    token = serializer.dumps(email, salt="email-confirm")
    verify_url = url_for("Users.EmailVerification", token=token, _external=True)
    html_message = html_msg(verify_url)
    msg = Message('Verify Your Email', recipients=[email])
    msg.html = html_message
    mail.send(msg)

# ============================
# ✅ Send Verification Endpoint
# ============================
@blp.route("/verify-email")
class SendVerificationEmail(MethodView):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        send_verification_email(user.user_email)
        return {"message": "Verification email sent successfully."}, 200

# ============================
# ✅ Email Confirmation Endpoint
# ============================
@blp.route("/verify/<token>", endpoint="EmailVerification")
class EmailVerification(MethodView):

    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(jwt_secret_key)
        try:
            return serializer.loads(token, salt="email-confirm", max_age=expiration)
        except (BadSignature, SignatureExpired):
            return False

    def get(self, token):
        email = self.confirm_token(token)
        if not email:
            return "Invalid or expired token", 400

        user = UserModel.query.filter_by(user_email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            return "Email successfully verified!", 200
        return "User not found", 404
    

# =====================
# ✅ User Registration
# =====================
@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        is_admin = False

        if UserModel.query.filter_by(user_email=user_data["user_email"]).first():
            abort(409, message="User with that email already exists.")

        if user_data["user_email"].find("vdojar.com") != -1:
            is_admin = True

        user = UserModel(
            user_first_name=user_data["user_first_name"],
            user_last_name=user_data["user_last_name"],
            user_email=user_data["user_email"],
            user_password=pbkdf2_sha256.hash(user_data["user_password"]),
            is_admin=is_admin,
            is_verified=False
        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while registering the user.")

        return {"message": "User registered successfully. Please check your email to verify your account."}, 201

# =================
# ✅ User Login
# =================
@blp.route("/login")
class UserLogin(MethodView):

    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(user_email=user_data["user_email"]).first()
        if user and pbkdf2_sha256.verify(user_data["user_password"], user.user_password):
            # if not user.is_verified:
            #     abort(403, message="Email not verified. Please check your inbox.")

            access_token = create_access_token(
                identity=str(user.user_id),
                fresh=True,
                additional_claims={"is_admin": user.is_admin}
            )
            return {"message": "Login successful", "access_token": access_token}, 200

        abort(401, message="Invalid credentials")

# ======================
# ✅ Get User + Videos
# ======================
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
                "is_admin": user.is_admin
            },
            "videos": [
                {
                    "video_id": video.video_id,
                    "video_filename": video.video_filename,
                    "video_title": video.video_title,
                    "video_description": video.video_description,
                    "video_genre": video.video_genre.split(",") if video.video_genre else [],
                    "thumbnails": video.thumbnail.to_dict()
                }
                for video in videos
            ]
        }

# ====================
# ✅ Logout Endpoint
# ====================
@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}


