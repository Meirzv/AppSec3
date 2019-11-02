from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

db.create_all()


class LoginUser(db.Model, UserMixin):
    __tablename__ = 'user'

    username = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    mfa = db.Column(db.String(80), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    pw_hash = db.Column(db.String)
    spell_query = db.Column(db.String, default=None)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_admin(self):
        return self.admin

    def is_anonymous(self):
        return False

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_spell_query(self, query):
        old_query = self.get_spell_query()
        if old_query is None:
            # first query for this user
            print("test first")
            self.spell_query = query
        else: #not the first query
            print("test second")
            new_query = str(old_query) + "," + query
            self.spell_query = new_query

    def get_spell_query(self):
        return self.spell_query