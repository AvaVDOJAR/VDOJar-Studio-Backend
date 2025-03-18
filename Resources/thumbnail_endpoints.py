from flask.views import MethodView
from flask import jsonify, request
from flask_smorest import Blueprint, abort #type:ignore
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from Models import ThumbnailModel
from database import db
from schemas import ThumbnailDetailsSchema
import cloudinary #type:ignore
import cloudinary.uploader  #type:ignore
from flask_jwt_extended import jwt_required


blp = Blueprint("Thumbnail_Details", __name__, description= "Operations on Thumbnail details")

@blp.route("/image")
class ThumbnailDetails(MethodView):


    
    def save_image_file(self,image_file):
        """Upload image to Cloudinary and return the URL"""
        try:
            upload_result = cloudinary.uploader.upload(image_file)
            return upload_result["secure_url"]  # Cloudinary-hosted URL
        except Exception as e:
            abort(500, message=f"Error uploading image: {str(e)}")
    

    @jwt_required()
    @blp.response(201)
    def post(self):
        # coming the path from the frontend
        if "image" not in request.files:
            abort(400, message="No image file uploaded")
        
        image_file= request.files["image"]
        if image_file.filename == "":
            abort(400, message="no selected image")
        
        
        video_id = request.form.get("video_id")

        if not video_id : 
            abort(400, message="Missing required fields: video_id")
        
        image_filename = self.save_image_file(image_file)

        thumbnail_details = ThumbnailModel(
            image_filename = image_filename,
            video_id = video_id
        )


        try:
            # path on which image get saved
            db.session.add(thumbnail_details)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()  # Rollback in case of failure
            abort(500, message=f"Error while uploading data")
        except IntegrityError:
            db.session.rollback()  # Rollback in case of failure
            abort(400, message=f"Duplicate Entity")
        
        return thumbnail_details.to_dict()


@blp.route("/image/<int:image_id>")
class GetThumbnail(MethodView):

    @jwt_required()
    @blp.response(200, ThumbnailDetailsSchema)
    def get(self, image_id):
        thumbnail_data = ThumbnailModel.query.get(image_id)

        if not thumbnail_data:
            abort(404, message="Image not Found")
        
        image_path = thumbnail_data.image_filename

        return jsonify({"image_url": thumbnail_data.image_filename})