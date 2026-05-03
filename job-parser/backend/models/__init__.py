from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    saved_vacancies = db.relationship('SavedVacancy', backref='user', lazy='dynamic')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }


class SavedVacancy(db.Model):
    __tablename__ = 'saved_vacancies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vacancy_id = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.String(255))
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    salary = db.Column(db.String(100))
    url = db.Column(db.String(500))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'vacancy_id', name='unique_user_vacancy'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'vacancy_id': self.vacancy_id,
            'company_id': self.company_id,
            'title': self.title,
            'company_name': self.company_name,
            'location': self.location,
            'salary': self.salary,
            'url': self.url,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }


class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(255))
    region = db.Column(db.String(255))
    filters = db.Column(db.Text)  # JSON string
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'region': self.region,
            'filters': self.filters,
            'searched_at': self.searched_at.isoformat() if self.searched_at else None
        }


class VacancyCache(db.Model):
    __tablename__ = 'vacancy_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    company_id = db.Column(db.String(255))
    data = db.Column(db.Text)  # JSON string
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vacancy_id': self.vacancy_id,
            'company_id': self.company_id,
            'data': self.data,
            'cached_at': self.cached_at.isoformat() if self.cached_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
