def html_msg(verify_url):
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            color: #28a745;
            font-size: 24px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 25px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #777;
        }}
        .footer a {{
            color: #28a745;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to VDOJAR Studio!</h2>
        <p>We're excited to have you with us. Please click the button below to verify your email address and get started:</p>
        <a href="{verify_url}" class="button">Verify Your Email</a>

        <div class="footer">
            <p>If you did not sign up for VDOJAR Studio, you can safely ignore this email.</p>
            <p>Thank you for choosing VDOJAR Studio!</p>
        </div>
    </div>
</body>
</html>
'''
