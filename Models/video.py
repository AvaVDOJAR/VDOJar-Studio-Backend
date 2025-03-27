from database import db

class VideoModel(db.Model): # type:ignore
    __tablename__ = "video_details"

    video_id = db.Column(db.Integer, primary_key=True)
    video_filename = db.Column(db.String(255), nullable=False, unique=True)
    video_title = db.Column(db.String(100), nullable=False)
    video_description = db.Column(db.String)
    video_genre = db.Column(db.String)  # Store the list of genres as a comma-separated string
    user_id = db.Column(db.Integer, db.ForeignKey("user_details.user_id"), nullable=False)
    is_approved = db.Column(db.Boolean, default = False)
    # Relationships
    user = db.relationship("UserModel", back_populates="videos")
    thumbnail = db.relationship("ThumbnailModel", back_populates="video", uselist=False, cascade="all, delete-orphan")


    def to_dict(self):
        return {
            "video_id": self.video_id,
            "video_filename": self.video_filename,
            "video_title": self.video_title,
            "video_description": self.video_description,
            "video_genre": self.video_genre.split(',') if self.video_genre else [],  # Convert string to list
            "is_approved": self.is_approved,
            "user_id": self.user_id,
            "thumbnail": self.thumbnail.to_dict() if self.thumbnail else None  # Include thumbnail info
        }