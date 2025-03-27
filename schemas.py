from marshmallow import fields, Schema, validate

class VideoDetailsSchema(Schema):
    video_id = fields.Str(dump_only=True)
    video_filename = fields.Str(dump_only=True)
    video_title = fields.Str(required=True)
    video_description = fields.Str()
    video_genre = fields.Str(required=True)
    user_id = fields.Int(required = True)
    is_approved = fields.Bool(dump_only = True)

class ThumbnailDetailsSchema(Schema):
    image_id = fields.Str(dump_only= True)
    image_filename = fields.Str(required=True)
    video_id = fields.Str(required=True)


class UserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    user_first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    user_last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    user_email = fields.Str(required=True, validate=validate.Email(error="Invalid email format"))
    user_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    user_email = fields.Str(required=True, validate=validate.Email(error="Invalid email format"))
    user_password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))


class VideoApproveSchema(Schema):
    user_id = fields.Int(required=True)
    video_id= fields.Int(required = True)
    is_approved = fields.Bool(required = True)


    
