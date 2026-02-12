class AuthService:
    def __init__(self, db):
        self.db = db

    def login(self, username, password):
        return self.db.verify_user(username, password)
