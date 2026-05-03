from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('parser', __name__)
db = None

@bp.route('/search', methods=['GET'])
def search_vacancies():
    """Search for vacancies"""
    from services.trudvsem_parser import parse_vacancies_list
    
    region_code = request.args.get('region', '')
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('pageSize', 10))
    profession = request.args.get('profession', '')
    search_query = request.args.get('query', '')
    
    result = parse_vacancies_list(
        region_code=region_code,
        page=page,
        page_size=page_size,
        profession=profession,
        search_query=search_query
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@bp.route('/vacancy/<vacancy_id>', methods=['GET'])
def get_vacancy(vacancy_id):
    """Get detailed vacancy information"""
    from services.trudvsem_parser import get_vacancy_detail
    
    company_id = request.args.get('companyId', '')
    
    if not company_id:
        return jsonify({"error": "companyId is required"}), 400
    
    result = get_vacancy_detail(company_id, vacancy_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@bp.route('/regions', methods=['GET'])
def get_regions_list():
    """Get list of regions"""
    from services.trudvsem_parser import get_regions
    
    regions = get_regions()
    return jsonify({"regions": regions}), 200


@bp.route('/save', methods=['POST'])
@jwt_required()
def save_vacancy():
    """Save a vacancy to user's favorites"""
    from models import SavedVacancy
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    vacancy_id = data.get('vacancy_id')
    company_id = data.get('company_id', '')
    title = data.get('title', '')
    company_name = data.get('company_name', '')
    location = data.get('location', '')
    salary = data.get('salary', '')
    url = data.get('url', '')
    
    if not vacancy_id:
        return jsonify({"error": "vacancy_id is required"}), 400
    
    # Check if already saved
    existing = db.session.execute(db.select(SavedVacancy).filter_by(user_id=user_id, vacancy_id=vacancy_id)).first()
    if existing:
        return jsonify({"error": "Vacancy already saved", "id": existing[0].id}), 409
    
    # Save vacancy
    saved = SavedVacancy(
        user_id=user_id,
        vacancy_id=vacancy_id,
        company_id=company_id,
        title=title,
        company_name=company_name,
        location=location,
        salary=salary,
        url=url
    )
    
    db.session.add(saved)
    db.session.commit()
    
    return jsonify({
        "message": "Vacancy saved successfully",
        "saved": {"id": saved.id, "vacancy_id": saved.vacancy_id, "title": saved.title}
    }), 201


@bp.route('/saved', methods=['GET'])
@jwt_required()
def get_saved_vacancies():
    """Get user's saved vacancies"""
    from models import SavedVacancy
    
    user_id = get_jwt_identity()
    
    results = db.session.execute(db.select(SavedVacancy).filter_by(user_id=user_id).order_by(SavedVacancy.saved_at.desc())).all()
    saved = [r[0] for r in results]
    
    return jsonify({
        "saved_vacancies": [{"id": s.id, "vacancy_id": s.vacancy_id, "company_id": s.company_id, "title": s.title, "company_name": s.company_name, "location": s.location, "salary": s.salary, "url": s.url, "saved_at": s.saved_at.isoformat() if s.saved_at else None} for s in saved]
    }), 200


@bp.route('/saved/<int:saved_id>', methods=['DELETE'])
@jwt_required()
def delete_saved_vacancy(saved_id):
    """Delete a saved vacancy"""
    from models import SavedVacancy
    
    user_id = get_jwt_identity()
    
    result = db.session.execute(db.select(SavedVacancy).filter_by(id=saved_id, user_id=user_id)).first()
    saved = result[0] if result else None
    
    if not saved:
        return jsonify({"error": "Saved vacancy not found"}), 404
    
    db.session.delete(saved)
    db.session.commit()
    
    return jsonify({"message": "Vacancy removed from saved"}), 200


@bp.route('/search-history', methods=['GET'])
@jwt_required()
def get_search_history():
    """Get user's search history"""
    from models import SearchHistory
    
    user_id = get_jwt_identity()
    limit = int(request.args.get('limit', 20))
    
    results = db.session.execute(db.select(SearchHistory).filter_by(user_id=user_id).order_by(SearchHistory.searched_at.desc()).limit(limit)).all()
    history = [r[0] for r in results]
    
    return jsonify({
        "search_history": [{"id": h.id, "query": h.query, "region": h.region, "filters": h.filters, "searched_at": h.searched_at.isoformat() if h.searched_at else None} for h in history]
    }), 200


@bp.route('/search-history', methods=['POST'])
@jwt_required()
def add_search_history():
    """Add search to history"""
    from models import SearchHistory
    import json
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    query = data.get('query', '')
    region = data.get('region', '')
    filters = json.dumps(data.get('filters', {}))
    
    history = SearchHistory(
        user_id=user_id,
        query=query,
        region=region,
        filters=filters
    )
    
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        "message": "Search added to history",
        "history": {"id": history.id, "query": history.query, "region": history.region}
    }), 201
