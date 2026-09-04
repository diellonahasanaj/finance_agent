# Thesis Documentation — Intelligent Personal Finance Advisor Agent

This document supports the Bachelor's thesis **"Development of an Intelligent Personal Finance Advisor Agent"**.

---

## 1. Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
│  React 18 + Vite + Material-UI + Recharts + React Router        │
│  Port: 5173                                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON (JWT Bearer)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND API (FastAPI)                        │
│  Port: 8000                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ Auth     │ │ Finance  │ │ Recommend.   │ │ Analysis        │ │
│  │ /auth/*  │ │ /finance/*│ │ /recommend.* │ │ /analysis/*     │ │
│  └──────────┘ └──────────┘ └──────────────┘ └─────────────────┘ │
│                             │                                    │
│  ┌──────────────────────────┴───────────────────────────────┐  │
│  │              SERVICE LAYER                                │  │
│  │  finance_service │ user_service │ recommendation_engine_v2 │  │
│  │  expense_classifier │ decision_engine │ expense_analysis    │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE (JSON files)                      │
│  users.json │ incomes.json │ expenses.json │ budgets.json       │
│  debts.json │ recommendations.json                               │
└─────────────────────────────────────────────────────────────────┘
```

### Design principles

- **Separation of concerns**: API routes delegate to service modules; UI pages call REST endpoints only.
- **Explainable AI**: Recommendations are rule-based with explicit IF–THEN logic and human-readable explanations.
- **JWT authentication**: Stateless bearer tokens; protected routes require valid token.
- **File-based storage**: Suitable for thesis demonstration without external database setup (MongoDB config exists for extended services).

---

## 2. Technologies Used

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18, TypeScript, Vite | SPA UI |
| UI | Material-UI (MUI) 5 | Components, theming, responsive layout |
| Charts | Recharts | Pie charts, line charts for analytics |
| HTTP | Axios | API client with JWT interceptors |
| Backend | FastAPI, Python 3.8+ | REST API |
| Auth | python-jose, passlib/bcrypt | JWT tokens, password hashing |
| Validation | Pydantic v2 | Request/response schemas |
| Testing | pytest, pytest-asyncio | Backend unit tests |
| Storage | JSON files (Motor/MongoDB optional) | User and financial data |

---

## 3. Installation Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm

### Backend

```bash
cd backend_python
pip install -r requirements.txt
# Configure backend_python/.env:
# MONGO_URI=mongodb://localhost:27017/personal_finance_advisor
# JWT_SECRET=your_jwt_secret_here
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
# Configure frontend/.env:
# VITE_API_URL=http://localhost:8000
npm run dev
```

Application: http://localhost:5173

### Demo account

Register at `/register` with a password containing uppercase, lowercase, number, and special character (e.g. `DemoPass1!`).

---

## 4. Database Schema (JSON Storage)

Data is keyed by user email in each file.

### users.json

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | Unique user ID (ObjectId) |
| `name` | string | Display name |
| `email` | string | Login email (lowercase key) |
| `hashed_password` | string | bcrypt hash |
| `is_verified` | boolean | Email verified flag |
| `monthly_income` | float? | User-declared income target |
| `savings_goal` | float? | Monthly savings target |
| `currency` | string | ISO currency code (USD, EUR, …) |
| `created_at` | datetime | Registration timestamp |

### expenses.json / incomes.json

Per-user arrays of records:

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | Record ID |
| `user_id` | string | Owner ID |
| `amount` | float | Transaction amount |
| `date` | string | ISO date (YYYY-MM-DD) |
| `category` | string | Expense category (expenses only) |
| `description` | string? | Expense description |
| `source` | string? | Income source |
| `classification_confidence` | float? | Auto-classification score |
| `created_at` | datetime | Creation timestamp |

### budgets.json

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Budget category |
| `limit` | float | Monthly limit |
| `month` | string | YYYY-MM |

### recommendations.json

Saved user bookmarks of AI recommendations with metadata (`saved_at`, `_id`).

---

## 5. API Endpoint Documentation

### Authentication (`/auth`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login, returns JWT |
| POST | `/auth/logout` | No | Client-side logout ack |
| GET | `/auth/me` | Yes | Current user profile |
| PUT | `/auth/profile` | Yes | Update name, income, savings goal, currency |
| POST | `/auth/change-password` | Yes | Change password |
| POST | `/auth/forgot-password` | No | Request password reset |
| POST | `/auth/reset-password` | No | Reset with token |

### Finance (`/finance`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET/POST | `/finance/income` | Yes | List / create income |
| PUT/DELETE | `/finance/income/{id}` | Yes | Update / delete income |
| GET/POST | `/finance/expense` | Yes | List / create expense |
| PUT/DELETE | `/finance/expense/{id}` | Yes | Update / delete expense |
| GET/POST | `/finance/budget` | Yes | List / set budget |
| GET | `/finance/dashboard?month=YYYY-MM` | Yes | Dashboard summary |
| GET | `/finance/analytics?months=6` | Yes | Chart data |
| GET | `/finance/transactions` | Yes | Paginated list (search, filter) |
| GET | `/finance/categories/statistics` | Yes | Category breakdown |
| POST | `/finance/ai-chat` | Yes | Natural-language financial Q&A |
| GET | `/finance/privacy/data-summary` | Yes | Data transparency |
| DELETE | `/finance/privacy/delete-data` | Yes | GDPR data deletion |

**Transaction query params**: `type`, `search`, `category`, `month`, `page`, `page_size`

### Recommendations (`/recommendations`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/recommendations/recommendations` | Yes | AI recommendations with explanations |
| POST | `/recommendations/recommendations/save` | Yes | Bookmark a recommendation |
| GET | `/recommendations/how-it-works` | Yes | Transparency documentation |
| GET | `/recommendations/categories` | Yes | Expense categories list |
| POST | `/recommendations/classify-expense` | Yes | Auto-categorize expense text |

---

## 6. AI Recommendation Logic

The advisor uses **rule-based intelligent analysis** (not opaque LLM output). Every recommendation follows:

```
IF <measurable condition from user data>
THEN <specific action>
BECAUSE <numeric explanation with amounts and percentages>
```

### Data inputs

1. Total income and expenses (all time or filtered)
2. Per-category spending breakdown
3. Monthly budgets vs actual spending
4. User profile: savings goal, monthly income target

### Rule categories

#### Budget overrun (HIGH priority)

```
IF spent(category) > budget_limit(category)
THEN recommend reducing category spending
EXPLANATION: "You exceeded your Food budget by 28% this month ($320 spent vs $250 budget).
              Reducing restaurant expenses by approximately $70 would allow you to stay
              within your planned monthly budget."
```

#### Budget warning (MEDIUM priority)

```
IF spent(category) > 80% of budget_limit(category)
THEN warn user to monitor remaining budget
```

#### Category threshold (MEDIUM priority)

```
IF category_spending / total_income > expert_threshold(category)
THEN suggest optimization
```

Thresholds: Food 15%, Transportation 10%, Housing 30%, Entertainment 10%, etc.

#### Savings rate (MEDIUM priority)

```
IF (income - expenses) < 20% of income
THEN recommend increasing savings with specific dollar amount
```

#### Negative cash flow (HIGH priority)

```
IF total_expenses > total_income
THEN warn about deficit with exact overage amount
```

### Expense auto-classification

Keyword matching in `expense_classifier.py` assigns categories (Food, Transportation, …) from transaction descriptions with a confidence score.

### AI chat assistant

The `/finance/ai-chat` endpoint uses pattern matching on user questions combined with live financial data to answer queries about balance, budgets, spending, and savings — always grounded in the user's actual numbers.

### Transparency guarantees

- Every recommendation includes `explanation`, `action_steps`, and `potential_savings`
- `/recommendations/how-it-works` documents the full pipeline
- `/transparency` page in the UI explains data usage
- No recommendation is generated without a triggering financial condition

---

## 7. Frontend Pages

| Route | Purpose |
|-------|---------|
| `/dashboard` | Overview cards, budget progress, alerts, recent transactions |
| `/transactions` | CRUD, search, filter, pagination |
| `/add-transaction` | Add income or expense |
| `/set-budget` | Create monthly category budgets |
| `/analytics` | Pie chart, trends, savings rate |
| `/recommendations` | Full AI recommendations with explanations |
| `/reports` | Reports + embedded AI chat |
| `/advisor` | Dedicated AI chat advisor |
| `/transparency` | How the AI works |
| `/settings` | Profile, password, currency, data deletion |

---

## 8. Testing

```bash
# Backend
cd backend_python
python -m pytest tests/

# Frontend production build
cd frontend
npm run build
```

Manual thesis demo flow:

1. Register → Login
2. Add income (Salary) and expenses (Food, Transport)
3. Set budgets for Food and Transport
4. View Dashboard — budget bars, alerts
5. Open Recommendations — verify explanations reference your numbers
6. Open Analytics — charts update
7. Use Advisor chat — ask "What's my balance?"
8. Edit profile in Settings — set EUR currency and savings goal

---

## 9. Completed vs Implemented Features

### Completed (thesis-ready)

- User registration, login, logout, JWT auth, protected routes
- Profile editing (name, monthly income, savings goal, currency)
- Password change
- Income/expense CRUD with auto-categorization
- Transaction list with search, filter, pagination
- Monthly budgets with progress and overrun alerts
- Dashboard with summary cards, recent transactions, savings progress
- Analytics charts (category pie, monthly trends)
- Rule-based AI recommendations with transparent explanations
- AI chat advisor grounded in user data
- Privacy/data summary and deletion
- Dark mode, loading/empty states, form validation

### Optional future extensions (not required for defense)

- MongoDB as primary store (partially wired in decision_engine)
- Real email delivery for verification/reset
- Bank API integration (Plaid)
- Multi-language UI

---

## 10. File Structure Reference

```
PersonalFinanceAgent/
├── backend_python/
│   ├── app/
│   │   ├── api/           # FastAPI routers
│   │   ├── services/      # Business logic & AI engines
│   │   ├── schemas/       # Pydantic models
│   │   └── utils/         # JWT, auth, password
│   ├── tests/
│   └── main.py
├── frontend/
│   └── src/
│       ├── pages/         # Route components
│       ├── components/    # Reusable UI
│       └── services/api.js
└── THESIS_DOCUMENTATION.md
```

---

*Generated for thesis defense preparation — Personal Finance Advisor Agent.*
