from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Fecha programada para la eliminación de la cuenta
    deletion_date = db.Column(db.DateTime, nullable=True)
    
    # Relación many-to-many para novelas leídas
    read_novels = db.relationship('Novel', secondary='user_read', backref='readers', lazy='dynamic')

    # Relación one-to-many para novelas creadas por el usuario
    novels = db.relationship('Novel', backref='author', lazy=True)


class UserRead(db.Model):
    __tablename__ = 'user_read'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True)
    favorite = db.Column(db.Boolean, default=False)


class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relación one-to-many con capítulos
    chapters = db.relationship('Chapter', backref='novel', lazy=True)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
