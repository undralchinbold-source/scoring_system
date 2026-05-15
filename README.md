# Scoring System API

Зээлийн оноо үнэлгээний систем — Flask + PostgreSQL + Machine Learning REST API.

## Технологи

- Python 3.12 / Flask 3.1
- PostgreSQL 16 (Docker)
- SQLAlchemy + Flask-Migrate
- JWT Authentication
- scikit-learn (Gradient Boosting) + joblib

## Төслийн бүтэц

```
scoring_system/
├── app/
│   ├── ml/                  ← ML Predictor класс (Singleton)
│   ├── routes/              ← API endpoints
│   ├── services/            ← Business logic
│   ├── validators/          ← Input шалгалт
│   └── models/              ← Database models
├── ml_model/
│   └── loan_scoring_model.pkl  ← Сургасан ML загвар
├── migrations/              ← Database migrations
├── tests/                   ← Unit тестүүд
├── postgres-stack/          ← Docker тохиргоо
├── requirements.txt
├── run.py
└── .env.example
```

## Суулгах заавар

### 1. Clone хийх
```bash
git clone https://github.com/undralchinbold-source/scoring_system.git
cd scoring_system
```

### 2. Virtual environment үүсгэх
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. .env файл үүсгэх
```bash
cp .env.example .env
```
`.env` файлд:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scoring_db
DB_USER=postgres
DB_PASSWORD=postgres
```

### 4. PostgreSQL Docker-оор эхлүүлэх
```bash
cd postgres-stack
docker compose up -d
cd ..
```

### 5. Database хүснэгт үүсгэх
```bash
flask db upgrade
```

### 6. Сервер асаах
```bash
python run.py
# http://127.0.0.1:5000
```

### 7. Тест ажиллуулах
```bash
python -m pytest tests/ -v
```

---

## API Endpoints

| Модуль | URL | Auth |
|---|---|---|
| Register | `POST /api/auth/register` | ✗ |
| Login | `POST /api/auth/login` | ✗ |
| **Predict** | `POST /api/predict` | ✓ |
| Users | `/api/users/` | ✓ |
| Clients | `/api/clients/` | ✓ |
| Loan Applications | `/api/loan-applications/` | ✓ |
| Score History | `/api/score-history/` | ✓ |
| Notifications | `/api/notifications/` | ✓ |
| Audit Logs | `/api/audit-logs/` | ✓ |

---

## ML Predict Endpoint

**POST** `/api/predict`

```json
{
  "monthly_income": 3000000,
  "employment_years": 5,
  "requested_amount": 10000000,
  "employment_type": "Инженер"
}
```

**Хариу:**
```json
{
  "score": 0.4826,
  "decision": "approved",
  "probabilities": {
    "approved": 0.4826,
    "manual_review": 0.515,
    "rejected": 0.0024
  },
  "model_version": "v1.0.0"
}
```

**employment_type утгууд:**
`Багш`, `Барилгачин`, `Бизнес эрхлэгч`, `Жолооч`, `Инженер`,
`Малчин`, `Тариаланч`, `Төрийн албан хаагч`, `Хувийн салбар`,
`Худалдагч`, `Эмч`, `Үйлчилгээ`

**decision утгууд:**
- `approved` — зөвшөөрсөн
- `manual_review` — гараар шалгах
- `rejected` — татгалзсан

---

## Postman

`scoring_system.postman_collection.json` файлыг Postman-д import хийж бүх API-г тестлэнэ.
