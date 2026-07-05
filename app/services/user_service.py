from app.models.user import User
from app.core.logger import logger


class UserService:

    def __init__(self, db):
        self.db = db

    def get_or_create_user(self, username: str):
        user = self.db.query(User).filter(
            User.username == username
        ).first()

        if user:
            return user

        user = User(
            username=username,
            password_hash="oauth_or_jwt_user"
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"Created new user record for '{username}'.")

        return user