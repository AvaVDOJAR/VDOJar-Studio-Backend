from database import db

class UserModel(db.Model): # type:ignore
    __tablename__ = "user_details"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_first_name = db.Column(db.String(100), nullable=False)
    user_last_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    user_password = db.Column(db.String(255), nullable=False)

    # One-to-Many relationship with VideoModel
    videos = db.relationship("VideoModel", back_populates="user", lazy="dynamic", cascade="all, delete")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_first_name": self.user_first_name,
            "user_last_name": self.user_last_name,
            "user_email": self.user_email,
            # "videos" : [vid.to_dict() for vid in self.videos] if self.videos else []
        }