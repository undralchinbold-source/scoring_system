# Scoring System — Frontend API Reference

Base URL: `http://127.0.0.1:5001`  
Content-Type: `application/json` (бүх request)  
Auth: `Authorization: Bearer <token>` (Login-аас бусад бүх endpoint)

---

## Authentication

### Нэвтрэх

```
POST /api/auth/login
```

**Request**
```json
{
  "email": "admin@scoring.mn",
  "password": "Admin1234!"
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGci...",
  "user": {
    "id": "d0062ab2-9f25-4266-a721-0b382cc4f707",
    "email": "admin@scoring.mn",
    "fullname": "Admin User",
    "role": "admin",
    "last_login": "2026-05-27T06:26:17.902767+00:00"
  }
}
```

**Response 401**
```json
{ "error": "Invalid email or password" }
```

**Frontend хэрэглэх жишээ:**
```js
const res = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
const { access_token, user } = await res.json()
localStorage.setItem('token', access_token)
```

> Token-ийн хүчинтэй хугацаа: **24 цаг**

---

## Эрхийн тогтолцоо

| Role | Унших | Үүсгэх / Засах / Устгах |
|---|---|---|
| `admin` | ✅ | ❌ |
| `super_user` | ✅ | ✅ |

Эрхгүй хүсэлт илгээхэд:
```json
// 401 — token байхгүй
{ "msg": "Missing Authorization Header" }

// 403 — эрх хүрэлцэхгүй
{ "error": "Forbidden" }
```

**Fetch helper:**
```js
const authFetch = (url, options = {}) =>
  fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      ...options.headers,
    },
  })
```

---

## Users `/api/users`

### Бүх хэрэглэгч авах
```
GET /api/users
```
**Response 200**
```json
[
  {
    "id": "d0062ab2-9f25-4266-a721-0b382cc4f707",
    "email": "admin@scoring.mn",
    "fullname": "Admin User",
    "role": "admin",
    "last_login": "2026-05-27T06:26:17+00:00"
  }
]
```

### Нэг хэрэглэгч авах
```
GET /api/users/:id
```

### Хэрэглэгч үүсгэх *(super_user)*
```
POST /api/users
```
**Request**
```json
{
  "email": "newuser@example.com",
  "password": "Password123!",
  "role": "admin",
  "fullname": "Шинэ Хэрэглэгч"
}
```
Roles: `"admin"` | `"super_user"`

**Response 201** — үүсгэсэн user object  
**Response 409** — `{ "error": "Email already exists" }`

### Хэрэглэгч засах *(super_user)*
```
PUT /api/users/:id
```
```json
{
  "fullname": "Шинэ нэр",
  "role": "super_user",
  "password": "NewPass123!"
}
```

### Хэрэглэгч устгах *(super_user)*
```
DELETE /api/users/:id
```
**Response 200** — `{ "message": "User deleted" }`

---

## Clients `/api/clients`

### Бүх клиент авах
```
GET /api/clients
```
**Response 200**
```json
[
  {
    "id": "...",
    "national_id": "ББ12345678",
    "fullname": "Батбаяр Дорж",
    "income": 2500000.0,
    "phone": "+97699001122",
    "created_by": "...",
    "created_at": "2026-05-27T06:00:00+00:00"
  }
]
```

### Нэг клиент авах
```
GET /api/clients/:id
```

### Клиент үүсгэх *(super_user)*
```
POST /api/clients
```
```json
{
  "national_id": "ББ12345678",
  "fullname": "Батбаяр Дорж",
  "income": 2500000,
  "phone": "+97699001122"
}
```
Заавал: `national_id`, `fullname`  
Сонголттой: `income`, `phone`

**Response 409** — `{ "error": "national_id already exists" }`

### Клиент засах *(super_user)*
```
PUT /api/clients/:id
```
```json
{
  "fullname": "Шинэ нэр",
  "income": 3000000,
  "phone": "+97699009900"
}
```

### Клиент устгах *(super_user)*
```
DELETE /api/clients/:id
```
**Response 409** — зээлийн өргөдөлтэй бол устгаж болохгүй:
```json
{ "error": "Cannot delete client with existing loan applications" }
```

---

## Loan Applications `/api/loan-applications`

### Бүх өргөдөл авах
```
GET /api/loan-applications
```
**Response 200**
```json
[
  {
    "id": "...",
    "client_id": "...",
    "user_id": "...",
    "requested_amount": 10000000.0,
    "status": "pending",
    "created_at": "2026-05-27T06:00:00+00:00",
    "updated_at": "2026-05-27T06:00:00+00:00"
  }
]
```

### Нэг өргөдөл авах
```
GET /api/loan-applications/:id
```

### Өргөдөл үүсгэх *(super_user)*
```
POST /api/loan-applications
```
```json
{
  "client_id": "uuid-of-client",
  "requested_amount": 10000000
}
```
Заавал: `client_id`, `requested_amount`  
Default status: `"pending"`

### Өргөдөл засах *(super_user)*
```
PUT /api/loan-applications/:id
```
```json
{
  "status": "approved",
  "requested_amount": 12000000
}
```
Status утгууд: `"pending"` | `"approved"` | `"rejected"` | `"cancelled"`

### Өргөдөл устгах *(super_user)*
```
DELETE /api/loan-applications/:id
```
> Score history болон notification cascade-аар устгагдана.

---

## ML Credit Scoring `/api/predict`

### Зээлийн оноо тооцоолох *(admin, super_user)*
```
POST /api/predict
```
**Request**
```json
{
  "application_id": "uuid-of-loan-application",
  "monthly_income": 2500000,
  "employment_years": 3.5,
  "requested_amount": 10000000,
  "employment_type": "Employed"
}
```

| Field | Төрөл | Заавал | Тайлбар |
|---|---|---|---|
| `application_id` | UUID string | ✅ | Урьдчилан үүссэн байх ёстой |
| `monthly_income` | number | ✅ | > 0 |
| `employment_years` | number | ✅ | Жилийн тоо |
| `requested_amount` | number | ✅ | > 0 |
| `employment_type` | string | ✅ | Доорх утгуудаас нэгийг сонгоно |

`employment_type` боломжит утгууд — моделиос хамаарна, жишээ нь:
`"Employed"`, `"Self-Employed"`, `"Unemployed"`

**Response 200**
```json
{
  "decision": "approved",
  "credit_score": 724,
  "score_range": { "min": 200, "max": 950 },
  "probabilities": {
    "approved": 0.6823,
    "rejected": 0.2105,
    "manual_review": 0.1072
  },
  "model_name": "Gradient Boosting",
  "model_version": "v1.0",
  "score_history_id": "uuid-of-saved-record"
}
```

| Field | Тайлбар |
|---|---|
| `decision` | `"approved"` \| `"rejected"` \| `"manual_review"` |
| `credit_score` | 200–950 оноо |
| `probabilities` | Бүх классын магадлал |
| `score_history_id` | Автоматаар хадгалсан ScoreHistory-ийн ID |

**Response 404** — `application_id` олдохгүй бол  
**Response 400** — талбар дутуу эсвэл буруу утга

---

## Score History `/api/score-history`

### Бүх оноо авах
```
GET /api/score-history
```
**Response 200**
```json
[
  {
    "id": "...",
    "application_id": "...",
    "model_version": "v1.0",
    "score": 724.0,
    "decision": "approved",
    "created_by": "...",
    "created_at": "2026-05-27T06:00:00+00:00"
  }
]
```

### Нэг оноо авах
```
GET /api/score-history/:id
```

### Оноо үүсгэх *(super_user)* — ихэвчлэн `/api/predict` автоматаар үүсгэдэг
```
POST /api/score-history
```
```json
{
  "application_id": "uuid",
  "model_version": "v1.0",
  "score": 720.0,
  "decision": "approved"
}
```

### Оноо засах / устгах *(super_user)*
```
PUT  /api/score-history/:id
DELETE /api/score-history/:id
```

---

## Notifications `/api/notifications`

### Бүх мэдэгдэл авах
```
GET /api/notifications
```
**Response 200**
```json
[
  {
    "id": "...",
    "application_id": "...",
    "channel": "email",
    "recipient": "client@example.com",
    "subject": "Зээлийн шийдвэр",
    "message_body": "Таны өргөдөл батлагдлаа.",
    "status": "pending",
    "sent_at": null
  }
]
```

### Мэдэгдэл үүсгэх *(super_user)*
```
POST /api/notifications
```
```json
{
  "application_id": "uuid",
  "channel": "email",
  "recipient": "client@example.com",
  "subject": "Зээлийн шийдвэр",
  "message_body": "Таны өргөдөл батлагдлаа."
}
```
Заавал: `channel`, `recipient`, `message_body`  
Сонголттой: `application_id`, `subject`

### Нэг / засах / устгах
```
GET    /api/notifications/:id
PUT    /api/notifications/:id
DELETE /api/notifications/:id
```

---

## Audit Logs `/api/audit-logs`

### Бүх log авах
```
GET /api/audit-logs
```
**Response 200**
```json
[
  {
    "id": "...",
    "user_id": "...",
    "action": "CREATE",
    "entity_type": "LoanApplication",
    "entity_id": "...",
    "created_at": "2026-05-27T06:00:00+00:00"
  }
]
```

### Log үүсгэх *(super_user)*
```
POST /api/audit-logs
```
```json
{
  "action": "CREATE",
  "entity_type": "LoanApplication",
  "entity_id": "uuid",
  "user_id": "uuid"
}
```
Заавал: `action`, `entity_type`

### Нэг / засах / устгах
```
GET    /api/audit-logs/:id
PUT    /api/audit-logs/:id
DELETE /api/audit-logs/:id
```

---

## HTTP Status Codes

| Code | Утга |
|---|---|
| 200 | Амжилттай |
| 201 | Амжилттай үүсгэгдлээ |
| 400 | Буруу request (талбар дутуу / буруу утга) |
| 401 | Token байхгүй эсвэл хүчингүй |
| 403 | Эрх хүрэлцэхгүй |
| 404 | Олдсонгүй |
| 409 | Давхардал (email / national_id аль хэдийн байна) |
| 500 | Server алдаа |

---

## Хурдан эхлэх жишээ (JavaScript)

```js
const API = 'http://127.0.0.1:5001'

// 1. Нэвтрэх
async function login(email, password) {
  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const data = await res.json()
  if (res.ok) localStorage.setItem('token', data.access_token)
  return data
}

// 2. Authenticated request хийх helper
async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      ...options.headers,
    },
  })
  if (res.status === 401) {
    // Token дууссан — нэвтрэх хуудас руу чиглүүлнэ
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
  return res.json()
}

// 3. Клиент авах
const clients = await api('/api/clients')

// 4. Зээлийн оноо тооцоолох
const result = await api('/api/predict', {
  method: 'POST',
  body: JSON.stringify({
    application_id: '...',
    monthly_income: 2500000,
    employment_years: 3.5,
    requested_amount: 10000000,
    employment_type: 'Employed',
  }),
})
console.log(result.credit_score, result.decision)
```

---

## Test хэрэглэгчид

| Email | Password | Role |
|---|---|---|
| `superuser@scoring.mn` | `Admin1234!` | `super_user` |
| `admin@scoring.mn` | `Admin1234!` | `admin` |
