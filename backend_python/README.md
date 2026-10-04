# Personal Finance Advisor Agent Backend (Python)

## Tech Stack
- FastAPI
- MongoDB (Motor async driver)
- Pydantic
- JWT Authentication (PyJWT)
- Bcrypt for password hashing
- Clean architecture
- Environment variables (.env)

## Project Structure
```
backend_python/
  main.py
  .env
  app/
    api/
      __init__.py
      auth.py
      finance.py
      analysis.py
      system.py
    core/
      app.py
      config.py
    models/
      user.py
      finance.py
    schemas/
      user.py
      finance.py
    services/
      user_service.py
      finance_service.py
      analysis_service.py
    utils/
      password.py
      jwt.py
      auth.py
    middleware/
      error_handler.py
```

## Endpoints
- `POST /auth/register` — Register
- `POST /auth/login` — Login
- `POST /finance/income` — Add income
- `POST /finance/expense` — Add expense
- `POST /finance/budget` — Set budget
- `POST /finance/debt` — Add debt
- `GET /analysis/monthly-summary?month=YYYY-MM` — Monthly summary
- `GET /system/disclaimer` — Disclaimer

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env` (optional - defaults are provided)
3. Start server: `python run.py`
4. API will be available at `http://localhost:8000`
5. View API documentation at `http://localhost:8000/docs`

## Features
- User registration and authentication with JWT
- Financial data management (income, expenses, budgets, debts)
- Monthly analysis with AI-powered recommendations
- RESTful API with automatic documentation
- Async MongoDB integration
- Comprehensive error handling
- Password security with bcrypt

---
This system provides educational financial suggestions and does not replace professional financial advice.
