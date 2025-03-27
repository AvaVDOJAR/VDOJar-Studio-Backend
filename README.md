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
