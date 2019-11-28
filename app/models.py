from flask_login import UserMixin
from sqlalchemy import Sequence

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
    logs_in = db.Column(db.String, default=None)
    logs_out = db.Column(db.String, default=None)
    spell_check = db.relationship('SpellCheck', backref='user', lazy=True)

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


    def get_logs_in(self):
        return self.logs_in

    def set_logs_in(self, logs_in):
        old_logs_in = self.get_logs_in()
        if old_logs_in is None:
            # first result for this user
            self.logs_in = logs_in
        else:  # not the first query
            new_logs_in = str(old_logs_in) + "{cut}" + logs_in
            self.logs_in = new_logs_in

    def get_logs_out(self):
        return self.logs_out

    def set_logs_out(self, logs_out):
        old_logs_out = self.get_logs_out()
        if old_logs_out is None:
            # first result for this user
            self.logs_out = logs_out
        else:  # not the first query
            new_logs_out = str(old_logs_out) + "{cut}" + logs_out
            self.logs_out = new_logs_out

    def del_last_logout_value(self):
        temp = self.logs_out.rfind("{cut}")
        if temp == -1:
            self.logs_out = None
        else:
            self.logs_out = self.logs_out[:temp]
        print(temp)


class SpellCheck(db.Model):
    __tablename__ = 'spell'

    query_id = db.Column(db.Integer, Sequence('query_id_seq'), primary_key=True)
    spell_query = db.Column(db.String, default=None)
    spell_result = db.Column(db.String, default=None)
    user_id = db.Column(db.String, db.ForeignKey('user.username'),
                          nullable=True)


    def set_spell_query(self, query):
        old_query = self.get_spell_query()
        if old_query is None:
            # first query for this user
            self.spell_query = query
        else:  # not the first query
            new_query = str(old_query) + "{cut}" + query
            self.spell_query = new_query

    def get_spell_query(self):
        return self.spell_query

    def set_spell_result(self, result):
        old_result = self.get_spell_result()
        if old_result is None:
            # first result for this user
            self.spell_result = result
        else:  # not the first query
            new_result = str(old_result) + "{cut}" + result
            self.spell_result = new_result

    def get_spell_result(self):
        return self.spell_result