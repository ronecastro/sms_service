from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import backref

@login.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except:
        return None
    
class User(UserMixin, db.Model):
    __tablename__ =  "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<{}, {}, {}>'.format(self.username,\
            self.email, self.phone)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __getitem__(self, key):
        if key == 'id':
            return self.id
        if key == 'username':
            return self.username
        if key == 'email':
            return self.email
        if key == 'phone':
            return self.phone

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notification = db.Column(db.String)
    last_sent = db.Column(db.DateTime, nullable=True)
    user =  db.relationship("User", backref=backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return '<{}>'.format(self.notification)

    def __getitem__(self, key):
        if key == 'id':
            return self.id
        if key == 'user_id':
            return self.user_id
        if key == 'notification':
            return self.notification
        if key == 'last_sent':
            return self.last_sent
        if key == 'user':
            return self.user

class Rule(db.Model):
    __tablename__ = "rules"
    id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Rule {}>'.format(self.rule)

    def __getitem__(self, key):
        if key == 'id':
            return self.id
        if key == 'rule':
            return self.rule
        if key == 'description':
            return self.description
