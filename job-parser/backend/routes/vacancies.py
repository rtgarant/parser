from flask import Blueprint, request, jsonify
from models import SavedVacancy, db

bp = Blueprint('vacancies', __name__)


@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get general statistics about vacancies"""
    # This is a placeholder - in production you would calculate real stats
    return jsonify({
        "total_regions": 85,
        "popular_professions": [
            {"name": "Водитель", "count": 15000},
            {"name": "Продавец", "count": 12000},
            {"name": "Повар", "count": 8000},
            {"name": "Сварщик", "count": 7500},
            {"name": "Электрик", "count": 6000}
        ]
    }), 200
