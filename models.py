from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)

    writer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, writer, content):
        self.writer = writer
        self.content = content

    def __repr__(self):
        return "<Message %r (Writer='%s')>" % (self.id, self.writer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    messages = db.relationship('Message',
                               backref=db.backref('writer', lazy='joined'),
                               lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha512', salt_length=16)

    def __repr__(self):
        return '<User %s>' % self.username

    def valid_password(self, password):
        return check_password_hash(self.password, password)