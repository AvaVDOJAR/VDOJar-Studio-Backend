from flask.views import MethodView
from flask import send_file, request
from flask_smorest import Blueprint, abort #type:ignore
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from Models import VideoModel
from database import db
from schemas import VideoApproveSchema
import os
import mimetypes
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt


blp = Blueprint("Video_Details", __name__, description= "Operations on video details")


@blp.route("/video")
class VideoDetails(MethodView):


    #  this is fro saving the file in local folder
    def save_video_file(self, video_file, destination_folder="VideoData"):
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        
        file_name = secure_filename(video_file.filename)
        destination_path = os.path.join(destination_folder, file_name)
        video_file.save(destination_path)

        return file_name
    
    

    @jwt_required()
    @blp.response(201)
    def post(self):
        # print("FILES:", request.files)  # Debugging
        # print("FORM:", request.form)    # Debugging

        if "video" not in request.files:
            abort(400, message="No video file uploaded")

        video = request.files["video"]
        if video.filename == "":
            abort(400, message="no selected video")

        # print(f"Received file: {video.filename}")
        
        video_file = request.files["video"]  # Get file from FormData
        video_title = request.form.get("video_title")
        video_description = request.form.get("video_description")
        video_genre = request.form.get("video_genre")
        user_id = request.form.get("user_id")


        if not video_title or not video_genre:
            abort(400, message="Missing required fields: video_title, video_genre")

        
        filename = self.save_video_file(video_file)  # Save file and get filename

        video_details = VideoModel(
            video_filename=filename,
            video_title=video_title,
            video_description=video_description,
            video_genre=video_genre,
            user_id = user_id,
        )
        # print(video_details)

        try:
            db.session.add(video_details)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Duplicate entry or invalid data")
        except SQLAlchemyError:
            abort(500, message="An error occurred while uploading the video")

        return video_details.to_dict()

    @jwt_required()
    @blp.response(200)  
    def get(self):
        videos = VideoModel.query.all()
        all_videos = []
        for vid in videos:
            video_data = {
                "user_id": vid.user_id,
                "video_description": vid.video_description,
                "video_filename": vid.video_filename,
                "video_genre": vid.video_genre,
                "video_id": vid.video_id,
                "video_title": vid.video_title,
                "thumbnail": vid.thumbnail.to_dict() if vid.thumbnail else None,  # FIXED
                "is_approved" : vid.is_approved
            }
            
            all_videos.append(video_data)



        return all_videos


@blp.route("/video/<int:video_id>")
class GetVideo(MethodView):

    @jwt_required()
    @blp.response(200)
    def get(self, video_id):
        video_data = VideoModel.query.get(video_id)

        if not video_data:
            abort(404, message="Video not found")
        
        video_path = os.path.join("VideoData", video_data.video_filename)

        if not os.path.exists(video_path):
            abort(404, message="video file is not in the server")
        
        mime_type = mimetypes.guess_type(video_path)[0]
        return send_file(video_path, mimetype= mime_type)
    
    @jwt_required()
    @blp.arguments(VideoApproveSchema)
    def post(self,video_data,video_id):
        claims = get_jwt()  # Get JWT claims
        if not claims.get("is_admin"):  # Check if user is admin
            abort(403, message="Admin access required")
        

        video = VideoModel.query.get_or_404(video_id)

        if video :
            # print(video_data["is_approved"])
            video.is_approved = video_data["is_approved"]
        else : 
            abort(404, message= "Video Not exist")
        
        db.session.add(video)
        db.session.commit()

        return video.to_dict()

