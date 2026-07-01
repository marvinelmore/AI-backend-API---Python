from app.auth.jwt_handler import create_access_token

def login_user(username: str):
    # fake user for now (we'll upgrade later)
    user_data = {
        "sub": username
    }

    token = create_access_token(user_data)
    return token