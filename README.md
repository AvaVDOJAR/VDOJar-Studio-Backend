# Flask App Setup

## Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Virtual environment (venv)

## Setup Instructions

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## Required Files

### `constant.py`
Create a `constant.py` file and add the following environment-specific variables:

```python
# Cloudinary Configuration
CLOUD_NAME = "your_cloud_name"
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Flask-JWT-Extended Configuration
JWT_SECRET_KEY = "your_jwt_secret_key"
```

### `blocklist.py`
Create a `blocklist.py` file to store revoked JWTs:

```python
BLOCKLIST = set()  # Blocklisted access tokens from JWT
```

## Running the Application

1. **Ensure the virtual environment is activated**
2. **Run the Flask application**
   ```sh
   flask run
   ```

## Dependencies
The required dependencies are listed in `requirements.txt`:

```
flask
flask-smorest
python-dotenv
sqlalchemy
flask-sqlalchemy
cloudinary
flask-jwt-extended
passlib
```

## Usage
- The API provides endpoints for user authentication, video uploads, and thumbnails.
- Tokens can be revoked by adding them to `BLOCKLIST`.
- Configure `constant.py` with appropriate values before running the app.

## Check Admin
- If the user logged in with vdojar mail id  then admin access get approved

# API Documentation

This document provides detailed information about the available endpoints and their usage.

## Table of Contents
- [Authentication](#authentication)
- [Email Verification](#email-verification)
- [Password Reset](#password-reset)
- [Video Management](#video-management)
- [Thumbnail Management](#thumbnail-management)

## Authentication

### Login
```
POST /auth/login
```

Send email and password to receive a JWT token.

**Request:**
```json
{
  "user_email": "user@example.com",
  "user_password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "your_jwt_token"
}
```

## Email Verification

### Send Verification Email
```
POST /users/verify-email
```

Sends an email to the logged-in user for verification.

### Verify Email
```
GET /users/verify/{token}
```

Click link from email to verify account.

## Password Reset

### Request OTP
```
POST /forgot-password/request
```

Sends a 6-digit OTP to the user's registered email.

**Request:**
```json
{
  "user_email": "user@example.com"
}
```

### Verify OTP
```
POST /forgot-password/verify
```

Checks if the OTP is correct and not expired.

**Request:**
```json
{
  "user_email": "user@example.com",
  "user_otp": "123456"
}
```

### Reset Password
```
POST /forgot-password/reset
```

Sets a new password using the valid OTP.

**Request:**
```json
{
  "user_email": "user@example.com",
  "user_otp": "123456",
  "user_password": "new_secure_password"
}
```

## Video Management

### Upload Video
```
POST /video/upload
```

Accepts video file upload (e.g., .mp4, .mov). Requires authentication and form-data with the file.

### Get User Videos
```
GET /video/user
```

Returns a list of videos uploaded by the authenticated user.

### Get All Videos
```
GET /video/all
```

Fetches all public videos in the platform.

## Thumbnail Management

### Upload Thumbnail
```
POST /thumbnail/upload
```

Accepts image upload for video thumbnail (e.g., .jpg, .png).

### Get Thumbnail
```
GET /thumbnail/{id}
```

Returns the thumbnail image for a given video.

## Additional Information

### OTP Details
- OTPs are valid for 10 minutes
- OTPs are cleared automatically after use or expiry