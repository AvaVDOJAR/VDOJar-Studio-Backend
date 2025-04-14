import random
from datetime import datetime, timedelta, timezone
from flask_smorest import Blueprint #type:ignore
from flask.views import MethodView
from flask_mail import Message #type:ignore

from Models import UserModel
from database import db
from extensions import mail
from schemas import UserEmailSchema, UserOTPVerifySchema, PasswordResetSchema
from passlib.hash import pbkdf2_sha256 #type:ignore


blp = Blueprint("PasswordReset", __name__, url_prefix="/forgot-password")

# Generate the OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP in HTML format
def send_otp_email(email, otp):
    html = f"""
    <html>
        <body>
            <h2>VDOJAR Studio - Password Reset</h2>
            <p>Your OTP for resetting the password is:</p>
            <h1 style="color:#28a745;">{otp}</h1>
            <p>This OTP is valid for 10 minutes.</p>
        </body>
    </html>
    """
    msg = Message("Password reset OTP", recipients=[email])
    msg.html = html
    mail.send(msg)

# Request the OTP
@blp.route("/request")
class SendOTP(MethodView):

    @blp.arguments(UserEmailSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(user_email=user_data["user_email"]).first()
        if not user:
            return {"message": "Email not registered."}, 404

        otp = generate_otp()
        hashed_otp = pbkdf2_sha256.hash(str(otp))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

        user.user_otp = hashed_otp
        user.otp_expiry = expiry
        db.session.commit()

        send_otp_email(user.user_email, otp)
        return {"message": "OTP sent to registered email."}, 200

# Verify the OTP
@blp.route("/verify")
class VerifyOTP(MethodView):

    @blp.arguments(UserOTPVerifySchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(user_email=user_data["user_email"]).first()

        if not user:
            return {"message": "User not found"}, 404

        if not user.otp_expiry or user.otp_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            user.user_otp = None
            user.otp_expiry = None
            db.session.commit()
            return {"message": "OTP expired"}, 400

        if pbkdf2_sha256.verify(user_data["user_otp"], user.user_otp):
            return {"message": "OTP verified"}, 200
        else:
            return {"message": "Invalid OTP"}, 400

# Reset Password
@blp.route("/reset")  # ✅ Added the missing @ symbol
class ResetPassword(MethodView):

    @blp.arguments(PasswordResetSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(user_email=user_data["user_email"]).first()

        if not user:
            return {"message": "User not found"}, 404

        if pbkdf2_sha256.verify(user_data["user_otp"], user.user_otp):
            user.user_password = pbkdf2_sha256.hash(user_data["user_password"])
            user.user_otp = None
            user.otp_expiry = None
            db.session.commit()
            return {"message": "Password reset successful"}, 200
        else:
            return {"message": "Invalid OTP"}, 400
