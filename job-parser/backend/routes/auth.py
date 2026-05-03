from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('auth', __name__)
db = None
bcrypt = None

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Validation
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required"}), 400
    
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if user exists
    from models import User
    if db.session.execute(db.select(User).filter_by(username=username)).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if db.session.execute(db.select(User).filter_by(email=email)).first():
        return jsonify({"error": "Email already exists"}), 409
    
    # Create new user
    user = User(username=username, email=email)
    user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "User registered successfully",
        "user": {"id": user.id, "username": user.username, "email": user.email},
        "access_token": access_token
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # Find user
    from models import User
    result = db.session.execute(db.select(User).filter_by(username=username)).first()
    user = result[0] if result else None
    
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "message": "Login successful",
        "user": {"id": user.id, "username": user.username, "email": user.email},
        "access_token": access_token
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    from models import User
    user_id = get_jwt_identity()
    result = db.session.execute(db.select(User).filter_by(id=user_id)).first()
    user = result[0] if result else None
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"user": {"id": user.id, "username": user.username, "email": user.email}}), 200


@bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    from models import User
    user_id = get_jwt_identity()
    result = db.session.execute(db.select(User).filter_by(id=user_id)).first()
    user = result[0] if result else None
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'username' in data:
        username = data['username']
        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        
        existing = db.session.execute(db.select(User).filter_by(username=username).filter(User.id != user.id)).first()
        if existing:
            return jsonify({"error": "Username already exists"}), 409
        
        user.username = username
    
    if 'email' in data:
        email = data['email']
        
        existing = db.session.execute(db.select(User).filter_by(email=email).filter(User.id != user.id)).first()
        if existing:
            return jsonify({"error": "Email already exists"}), 409
        
        user.email = email
    
    if 'password' in data:
        password = data['password']
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }), 200
