import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re

BASE_URL = "https://trudvsem.ru"
VACANCIES_LIST_URL = "https://trudvsem.ru/iblocks/_catalog/flat_filter_prr_search_vacancies/data"
VACANCY_DETAIL_URL = "https://trudvsem.ru/iblocks/job_card"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://trudvsem.ru/',
    'Origin': 'https://trudvsem.ru'
}


def parse_vacancies_list(region_code="", page=0, page_size=10, profession="", search_query=""):
    """
    Parse list of vacancies from trudvsem.ru
    
    Args:
        region_code: Region code filter (e.g., "77" for Moscow)
        page: Page number (0-indexed)
        page_size: Number of results per page
        profession: Profession/professional area filter
        search_query: Free text search query
    
    Returns:
        dict: Parsed vacancies data
    """
    # Build filter object
    filter_obj = {
        "regionCode": [region_code] if region_code else [""],
        "publishDateTime": ["EXP_0"]  # All time
    }
    
    # Add profession filter if provided
    if profession:
        filter_obj["professionCode"] = [profession]
    
    params = {
        'filter': json.dumps(filter_obj),
        'orderColumn': 'RELEVANCE_DESC',
        'page': page,
        'pageSize': page_size
    }
    
    # Add search query if provided
    if search_query:
        params['searchQuery'] = search_query
    
    try:
        response = requests.get(VACANCIES_LIST_URL, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the response
        vacancies = []
        total_count = 0
        
        if 'data' in data:
            items = data['data'].get('items', [])
            total_count = data['data'].get('total', 0)
            
            for item in items:
                vacancy = parse_vacancy_item(item)
                if vacancy:
                    vacancies.append(vacancy)
        
        return {
            'success': True,
            'vacancies': vacancies,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size if page_size > 0 else 0
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'vacancies': [],
            'total': 0
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f"Invalid JSON response: {str(e)}",
            'vacancies': [],
            'total': 0
        }


def parse_vacancy_item(item):
    """Parse a single vacancy item from the list"""
    try:
        vacancy = {
            'vacancy_id': item.get('id', ''),
            'company_id': item.get('companyId', ''),
            'title': item.get('name', ''),
            'company_name': item.get('companyName', ''),
            'location': item.get('regionName', ''),
            'address': item.get('address', ''),
            'salary': format_salary(
                item.get('salaryMin', 0),
                item.get('salaryMax', 0),
                item.get('salaryCurrency', 'RUB')
            ),
            'salary_min': item.get('salaryMin', 0),
            'salary_max': item.get('salaryMax', 0),
            'salary_currency': item.get('salaryCurrency', 'RUB'),
            'published_date': item.get('publishDate', ''),
            'url': f"https://trudvsem.ru/vacancy/{item.get('id', '')}",
            'has_remote': item.get('isRemote', False),
            'experience': item.get('experience', ''),
            'employment': item.get('employment', ''),
        }
        return vacancy
    except Exception as e:
        print(f"Error parsing vacancy item: {e}")
        return None


def format_salary(min_salary, max_salary, currency='RUB'):
    """Format salary for display"""
    if min_salary == 0 and max_salary == 0:
        return "По договорённости"
    
    currency_symbol = '₽' if currency == 'RUB' else currency
    
    if min_salary == max_salary:
        return f"{min_salary:,} {currency_symbol}"
    elif min_salary > 0 and max_salary > 0:
        return f"от {min_salary:,} до {max_salary:,} {currency_symbol}"
    elif min_salary > 0:
        return f"от {min_salary:,} {currency_symbol}"
    else:
        return f"до {max_salary:,} {currency_symbol}"


def get_vacancy_detail(company_id, vacancy_id):
    """
    Get detailed information about a specific vacancy
    
    Args:
        company_id: Company ID
        vacancy_id: Vacancy ID
    
    Returns:
        dict: Detailed vacancy information
    """
    params = {
        'companyId': company_id,
        'vacancyId': vacancy_id
    }
    
    try:
        response = requests.get(VACANCY_DETAIL_URL, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the detailed vacancy data
        vacancy_detail = parse_vacancy_detail(data)
        
        return {
            'success': True,
            'data': vacancy_detail
        }
        
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'data': None
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f"Invalid JSON response: {str(e)}",
            'data': None
        }


def parse_vacancy_detail(data):
    """Parse detailed vacancy information"""
    try:
        if not data or 'data' not in data:
            return None
        
        item = data['data']
        
        detail = {
            'vacancy_id': item.get('id', ''),
            'company_id': item.get('companyId', ''),
            'title': item.get('name', ''),
            'company_name': item.get('companyName', ''),
            'description': item.get('description', ''),
            'requirements': item.get('requirements', ''),
            'responsibilities': item.get('responsibilities', ''),
            'conditions': item.get('conditions', ''),
            'location': item.get('regionName', ''),
            'address': item.get('address', ''),
            'salary': format_salary(
                item.get('salaryMin', 0),
                item.get('salaryMax', 0),
                item.get('salaryCurrency', 'RUB')
            ),
            'salary_min': item.get('salaryMin', 0),
            'salary_max': item.get('salaryMax', 0),
            'salary_currency': item.get('salaryCurrency', 'RUB'),
            'published_date': item.get('publishDate', ''),
            'updated_date': item.get('updateDate', ''),
            'url': f"https://trudvsem.ru/vacancy/{item.get('id', '')}",
            'has_remote': item.get('isRemote', False),
            'experience': item.get('experience', ''),
            'employment': item.get('employment', ''),
            'schedule': item.get('schedule', ''),
            'education': item.get('education', ''),
            'contacts': {
                'email': item.get('contactEmail', ''),
                'phone': item.get('contactPhone', ''),
                'contact_person': item.get('contactPerson', '')
            },
            'company_info': {
                'name': item.get('companyName', ''),
                'description': item.get('companyDescription', ''),
                'industry': item.get('companyIndustry', ''),
                'website': item.get('companyWebsite', '')
            }
        }
        
        return detail
        
    except Exception as e:
        print(f"Error parsing vacancy detail: {e}")
        return None


def get_regions():
    """Get list of Russian regions"""
    # Common regions with their codes
    regions = [
        {"code": "", "name": "Вся Россия"},
        {"code": "77", "name": "Москва"},
        {"code": "78", "name": "Санкт-Петербург"},
        {"code": "50", "name": "Московская область"},
        {"code": "47", "name": "Ленинградская область"},
        {"code": "52", "name": "Нижегородская область"},
        {"code": "66", "name": "Свердловская область"},
        {"code": "74", "name": "Челябинская область"},
        {"code": "63", "name": "Самарская область"},
        {"code": "54", "name": "Новосибирская область"},
        {"code": "23", "name": "Краснодарский край"},
        {"code": "59", "name": "Пермский край"},
        {"code": "34", "name": "Волгоградская область"},
        {"code": "61", "name": "Ростовская область"},
        {"code": "16", "name": "Республика Татарстан"},
        {"code": "02", "name": "Республика Башкортостан"},
        {"code": "64", "name": "Саратовская область"},
        {"code": "55", "name": "Омская область"},
        {"code": "38", "name": "Иркутская область"},
        {"code": "24", "name": "Красноярский край"},
        {"code": "22", "name": "Алтайский край"},
        {"code": "42", "name": "Кемеровская область"},
        {"code": "72", "name": "Тюменская область"},
        {"code": "36", "name": "Воронежская область"},
        {"code": "76", "name": "Ярославская область"},
        {"code": "56", "name": "Оренбургская область"},
        {"code": "40", "name": "Калужская область"},
        {"code": "33", "name": "Владимирская область"},
        {"code": "28", "name": "Амурская область"},
        {"code": "25", "name": "Приморский край"},
        {"code": "27", "name": "Хабаровский край"},
        {"code": "41", "name": "Камчатский край"},
        {"code": "35", "name": "Вологодская область"},
        {"code": "39", "name": "Калининградская область"},
        {"code": "86", "name": "Ханты-Мансийский АО"},
        {"code": "87", "name": "Чукотский АО"},
        {"code": "89", "name": "Ямало-Ненецкий АО"},
        {"code": "91", "name": "Республика Крым"},
        {"code": "92", "name": "Севастополь"},
    ]
    return regions
