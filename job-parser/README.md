# Job Parser Platform

Платформа для парсинга вакансий с сайта trudvsem.ru с системой авторизации и аккаунтов.

## Структура проекта

```
job-parser/
├── backend/
│   ├── app.py              # Основное приложение Flask
│   ├── requirements.txt    # Зависимости Python
│   ├── .env               # Переменные окружения
│   ├── models/            # Модели базы данных
│   │   └── __init__.py
│   ├── routes/            # API маршруты
│   │   ├── auth.py        # Авторизация
│   │   ├── parser.py      # Парсинг вакансий
│   │   └── vacancies.py   # Дополнительный функционал
│   ├── services/          # Бизнес-логика
│   │   └── trudvsem_parser.py  # Парсер trudvsem.ru
│   └── utils/             # Утилиты
└── frontend/
    └── index.html         # Single Page Application
```

## Установка

### Backend

1. Перейдите в директорию backend:
```bash
cd job-parser/backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения (файл .env уже создан):
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///jobparser.db
DEBUG=True
```

5. Запустите сервер:
```bash
python app.py
```

Сервер запустится на http://localhost:5000

### Frontend

Просто откройте файл `frontend/index.html` в браузере или используйте любой статический веб-сервер.

## API Endpoints

### Авторизация
- `POST /api/auth/register` - Регистрация нового пользователя
- `POST /api/auth/login` - Вход пользователя
- `GET /api/auth/me` - Получение информации о текущем пользователе
- `PUT /api/auth/update-profile` - Обновление профиля

### Парсинг вакансий
- `GET /api/parser/search` - Поиск вакансий
  - Параметры: region, page, pageSize, profession, query
- `GET /api/parser/vacancy/<vacancy_id>` - Получение деталей вакансии
  - Параметры: companyId
- `GET /api/parser/regions` - Список регионов

### Сохранённые вакансии (требует авторизации)
- `POST /api/parser/save` - Сохранить вакансию
- `GET /api/parser/saved` - Получить сохранённые вакансии
- `DELETE /api/parser/saved/<id>` - Удалить из сохранённых

### История поиска (требует авторизации)
- `GET /api/parser/search-history` - Получить историю поиска
- `POST /api/parser/search-history` - Добавить в историю поиска

## Функционал

### Для всех пользователей:
- Поиск вакансий по регионам
- Фильтрация по поисковому запросу
- Просмотр деталей вакансии
- Пагинация результатов

### Для зарегистрированных пользователей:
- Сохранение вакансий в избранное
- История поисковых запросов
- Управление профилем

## Технологии

**Backend:**
- Flask - веб-фреймворк
- Flask-SQLAlchemy - ORM
- Flask-JWT-Extended - JWT авторизация
- Flask-Bcrypt - Хеширование паролей
- Requests - HTTP-запросы к trudvsem.ru

**Frontend:**
- Vanilla JavaScript
- TailwindCSS - стилизация
- Font Awesome - иконки

## Примечание

Данный проект использует API сайта trudvsem.ru для парсинга вакансий. Убедитесь, что вы соблюдаете условия использования сайта и не превышаете разумные лимиты запросов.
