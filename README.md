# Scoring System API

Зээлийн оноо үнэлгээний систем — Flask + PostgreSQL REST API.

## Технологи

- Python 3.14 / Flask 3.1
- PostgreSQL 16 (Docker)
- SQLAlchemy + Flask-Migrate

## Ажиллуулах

**1. Clone хийх**
```bash
git clone https://github.com/undralchinbold-source/scoring_system.git
cd scoring_system
```

**2. Virtual environment үүсгэх**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. .env файл үүсгэх**
```bash
cp .env.example .env
# .env файлд өөрийн DB мэдээллийг оруулна
```

**4. PostgreSQL database үүсгэх**
```bash
# Docker ашиглан:
docker run --name postgres16 -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin123 -e POSTGRES_DB=scoring_db -p 5432:5432 -d postgres:16
```

**5. Migration ажиллуулах**
```bash
flask db upgrade
```

**6. Сервер асаах**
```bash
python run.py
# http://127.0.0.1:5000
```

## API Endpoints

| Модуль | URL |
|---|---|
| Users | `/api/users/` |
| Clients | `/api/clients/` |
| Loan Applications | `/api/loan-applications/` |
| Score History | `/api/score-history/` |
| Notifications | `/api/notifications/` |
| Audit Logs | `/api/audit-logs/` |

Дэлгэрэнгүй тест: `scoring_system.postman_collection.json` файлыг Postman-д import хийнэ.
