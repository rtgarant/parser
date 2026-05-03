from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///jobparser.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    
    # Initialize extensions
    db = SQLAlchemy()
    bcrypt = Bcrypt()
    jwt = JWTManager()
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Register routes
    from routes import auth, vacancies, parser
    
    # Pass db to routes
    auth.db = db
    auth.bcrypt = bcrypt
    parser.db = db
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(vacancies.bp, url_prefix='/api/vacancies')
    app.register_blueprint(parser.bp, url_prefix='/api/parser')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return jsonify({"message": "Job Parser API is running", "version": "1.0.0"})
    
    @app.route('/api/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
