from database import db

class ThumbnailModel(db.Model): # type:ignore
    __tablename__ = "thumbnail_details"

    image_id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("video_details.video_id"), nullable=False, unique=True)

    # Correct bidirectional relationship
    video = db.relationship("VideoModel", back_populates="thumbnail")

    def to_dict(self):
        return {
            "image_id": self.image_id,
            "image_filename": self.image_filename,
            "video_id": self.video_id
        }
