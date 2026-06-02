# Personal Finance Advisor Agent - Thesis Project Documentation

## Project Overview

**Title:** Development of an Intelligent Agent for Personal Financial Advisory (Personal Finance Advisor Agent)

**Objective:** Build a simple but functional AI-powered financial advisor system focused on personal budget management, expense analysis, and financial recommendations, specifically designed for a diploma thesis project.

**Key Focus Areas:**
- Personal expense and budget management
- Intelligent spending behavior analysis
- Rule-based financial recommendations with transparency
- Budget overrun detection and alerts
- Educational financial guidance (NOT investment advice)
- Privacy-first data handling

---

## Project Architecture

### Backend Structure

```
backend_python/
├── app/
│   ├── api/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── finance.py           # Financial data CRUD
│   │   ├── analysis.py          # Analysis endpoints
│   │   ├── recommendations.py   # Recommendation endpoints (NEW)
│   │   ├── system.py            # System endpoints
│   │   └── testing.py           # Testing endpoints
│   ├── core/
│   │   ├── app.py               # FastAPI app factory
│   │   └── config.py            # Configuration
│   ├── middleware/
│   │   └── error_handler.py     # Error handling
│   ├── models/
│   │   ├── user.py              # User models
│   │   └── finance.py           # Financial models
│   ├── schemas/
│   │   ├── user.py              # User schemas
│   │   └── finance.py           # Finance schemas
│   ├── services/
│   │   ├── user_service.py
│   │   ├── finance_service.py
│   │   ├── analysis_service.py
│   │   ├── expense_classifier.py      # NEW: Expense classification
│   │   ├── recommendation_engine_v2.py # NEW: Rule-based recommendations
│   │   └── budget_analysis_service.py  # NEW: Budget analysis
│   └── utils/
│       ├── auth.py
│       ├── jwt.py
│       ├── password.py
│       └── email.py
├── run.py                       # Entry point
└── requirements.txt             # Dependencies
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/                # Auth components
│   │   ├── dashboard/           # Dashboard components
│   │   ├── forms/               # Form components
│   │   └── layout/
│   │       ├── SideBar.tsx      # Updated with new routes
│   │       └── ProfessionalLayout.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx        # Dashboard
│   │   ├── AddExpense.tsx       # Add expense
│   │   ├── SetBudget.tsx        # Budget management
│   │   ├── Recommendations.tsx  # NEW: AI recommendations
│   │   ├── Analytics.tsx        # NEW: Analytics dashboard
│   │   ├── Transparency.tsx     # NEW: How it works
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── ForgotPassword.tsx
│   │   ├── ResetPassword.tsx
│   │   ├── AddTransaction.tsx
│   │   └── Reports.tsx
│   ├── services/
│   │   ├── api.js              # API client
│   │   └── index.ts
│   └── theme/
│       └── theme.ts            # Material-UI theme
```

---

## Core Components

### 1. Expense Classification Service (`expense_classifier.py`)

**Purpose:** Automatically categorizes expenses using keyword matching.

**Categories:**
- Food
- Transportation
- Housing
- Utilities
- Entertainment
- Health
- Education
- Shopping
- Other

**Algorithm:**
1. Combine title and description into searchable text
2. Match against category keywords
3. Return (category, confidence_score)
4. Default to "Other" if no match

**Example:**
```python
classifier.classify_expense("Starbucks coffee", "Daily morning coffee")
# Returns: ('Food', 0.8)
```

### 2. Recommendation Engine (`recommendation_engine_v2.py`)

**Purpose:** Generate rule-based financial recommendations with detailed explanations.

**Recommendation Types:**
- Savings
- Debt Reduction
- Spending Optimization
- Warning
- Budget Alert

**Rule-Based Logic Examples:**

```
IF entertainment_spending > 30% of total_income
THEN Generate recommendation: "Reduce entertainment spending"
EXPLANATION: "Entertainment represents X% of income. Industry standard is 10%."

IF total_expenses > monthly_budget
THEN Generate alert: "Budget exceeded"
EXPLANATION: "Spend ${excess} over budget"

IF savings_rate < 20%
THEN Generate recommendation: "Increase savings"
EXPLANATION: "Current savings: X%. Target: 20%"
```

**Key Features:**
- Every recommendation includes:
  - Title
  - Recommendation text
  - Detailed explanation
  - Potential savings estimate
  - Priority level (high/medium/low)
  - Action steps
  - Category

### 3. Budget Analysis Service (`budget_analysis_service.py`)

**Purpose:** Analyzes spending against budgets and detects anomalies.

**Alert Levels:**
- INFO: ✅ Budget on track
- WARNING: 🟡 80%+ of budget used
- DANGER: 🔴 95%+ of budget used
- CRITICAL: ⛔ Budget exceeded

**Outputs:**
- Category-wise budget status
- Alert messages
- Spending anomalies
- Trend analysis
- Recommendations

### 4. API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

#### Financial Data
- `GET /finance/expense` - Get all expenses
- `POST /finance/expense` - Create expense
- `GET /finance/budget` - Get budgets
- `POST /finance/budget` - Create budget

#### Recommendations
- `GET /recommendations/recommendations` - Get AI recommendations
- `POST /recommendations/recommendations/save` - Save recommendation
- `GET /recommendations/history` - Get recommendation history
- `GET /recommendations/categories` - Get expense categories
- `POST /recommendations/classify-expense` - Classify expense
- `GET /recommendations/how-it-works` - Get transparency info

#### Analytics
- `GET /finance/dashboard` - Dashboard summary with analytics

---

## Frontend Pages

### 1. Dashboard
**Components:**
- Summary cards (Net Income, Total Income, Total Expenses, Debts)
- Recent transactions
- AI Financial Insights
- Budget progress
- Month selector

**Features:**
- Real-time data refresh
- Responsive design
- Loading states
- Error handling

### 2. Recommendations Page
**Components:**
- Recommendation count summary
- High-priority alerts
- Potential monthly savings
- Recommendation cards with:
  - Title and type
  - Priority badge
  - Expandable details
  - Explanation section
  - Potential savings
  - Action steps
- Save recommendation button
- Ethical disclaimer

**Features:**
- Expandable recommendation details
- Category-based filtering (implicit)
- Sort by priority
- Visual indicators

### 3. Analytics Page
**Visualizations:**
- Savings rate metric
- Budget usage metric
- Spending by category (Pie chart)
- Category breakdown (Progress bars)
- Monthly trends (Line chart)
- Key insights

**Features:**
- Responsive charts using Recharts
- Multiple chart types
- Key financial metrics
- Trend analysis

### 4. Transparency/How It Works Page
**Sections:**
1. The AI Advisory Process (6 steps with explanations)
2. Ethical Commitment (6+ guidelines)
3. FAQ (5 common questions)
4. Legal Disclaimer
5. Privacy & Security section

**Purpose:**
- Educate users about the system
- Build trust through transparency
- Explain limitations and ethics
- Clarify it's NOT financial advice

---

## Key Features

### Ethical & Transparency Layer

**Disclaimer:**
"This system provides educational financial suggestions and does not replace professional financial advice."

**Guidelines:**
- ✅ All recommendations are transparent and explainable
- ✅ You control which recommendations to implement
- ✅ Your financial data is private and secure
- ✅ Recommendations are educational, not financial advice
- ✅ No risky or high-risk financial advice is given
- ✅ You should consult a professional before major financial decisions

### Budget Management
- Set monthly budget limits per category
- Track spending vs. budget in real-time
- Visual progress bars
- Automatic alerts at 80%, 95%, 100%

### Expense Analysis
- Automatic expense categorization
- Spending pattern analysis
- Trend detection (increasing/decreasing)
- Category-wise breakdown

### Recommendations
- Rule-based generation (no ML)
- Detailed explanations for every recommendation
- Potential savings estimates
- Actionable steps
- Priority levels
- Category-specific advice

---

## Technical Stack

### Backend
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Database:** MongoDB (with Motor async driver)
- **Authentication:** JWT tokens, bcrypt
- **Language:** Python 3.13

### Frontend
- **Framework:** React 18 + TypeScript
- **UI Library:** Material-UI (MUI)
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **Animations:** Framer Motion
- **Build Tool:** Vite

---

## Data Models

### User Model
```python
{
    _id: ObjectId,
    name: str,
    email: EmailStr,
    hashed_password: str,
    created_at: datetime
}
```

### Expense Model
```python
{
    _id: ObjectId,
    user_id: str,
    amount: float,
    category: str,           # Auto-classified
    description: str (optional),
    date: str,
    subcategory: str (optional),
    payment_method: str (optional),
    is_essential: bool,
    tags: List[str],
    created_at: datetime
}
```

### Budget Model
```python
{
    _id: ObjectId,
    user_id: str,
    category: str,
    limit: float,
    month: str,              # YYYY-MM
    spent: float,
    warning_threshold: float,  # 0.80 = 80%
    created_at: datetime
}
```

### Recommendation Model
```python
{
    _id: ObjectId,
    user_id: str,
    type: str,               # Savings, Debt Reduction, etc.
    title: str,
    recommendation: str,
    explanation: str,
    priority: str,           # high, medium, low
    category: str,
    potential_savings: float (optional),
    action_steps: List[str],
    created_at: datetime
}
```

---

## Running the Application

### Backend
```bash
cd backend_python
python run.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install    # First time only
npm run dev    # Development server
# Frontend runs on http://localhost:5173
```

---

## Testing Scenarios

### Scenario 1: User Exceeds Budget
1. Set Food budget: $500
2. Add expenses totaling $550
3. System generates:
   - ⛔ Budget exceeded alert
   - Recommendation to reduce food spending
   - Explanation of excess: $50 over budget

### Scenario 2: Savings Too Low
1. Income: $3000, Expenses: $2700
2. Savings rate: 10%
3. System generates:
   - Recommendation: "Increase savings"
   - Target: 20% = $600/month
   - Action steps to reduce spending

### Scenario 3: High Entertainment Spending
1. Income: $3000, Entertainment: $900 (30%)
2. System generates:
   - Recommendation: "Reduce entertainment"
   - Explanation: "35% of expenses vs. 10% recommended"
   - Potential savings: $200-300/month

### Scenario 4: Spending Pattern Change
1. Historical: Food $400/month average
2. Current: Food $600/month
3. System generates:
   - Anomaly alert: 50% increase detected
   - Recommendation: Review recent food purchases

---

## Security & Privacy

### Data Protection
- All passwords hashed with bcrypt
- JWT authentication with token expiration
- CORS enabled for frontend
- Error messages don't expose system details

### Privacy Measures
- Financial data stored securely
- No data sharing with third parties
- User data isolated by user_id
- Sensitive operations require authentication

---

## Future Enhancements

1. **Machine Learning:**
   - Natural language processing for better expense classification
   - Spending pattern prediction
   - Anomaly detection

2. **Advanced Features:**
   - Bill reminders
   - Savings goals tracking
   - Investment recommendations (with disclaimers)
   - Multi-user support (families)
   - Export to PDF reports

3. **Integrations:**
   - Bank account connections
   - Email notifications
   - Calendar integration for recurring expenses

4. **Analytics:**
   - Year-over-year comparisons
   - Budget forecasting
   - Peer comparison (anonymized)

---

## Project Completion Checklist

✅ Expense classification system
✅ Rule-based recommendation engine
✅ Budget analysis and alerts
✅ Ethical & transparency layer
✅ API endpoints (complete CRUD)
✅ Dashboard page (enhanced)
✅ Recommendations page (new)
✅ Analytics page (new)
✅ Transparency/How It Works page (new)
✅ SideBar navigation (updated)
✅ Responsive UI design
✅ Error handling
✅ Data validation
✅ Security (JWT, hashing)

---

## Thesis Project Suitability

This project is ideal for a diploma thesis because it:

1. **Demonstrates Full-Stack Development:** Both backend and frontend with modern frameworks
2. **Shows System Design:** Well-organized architecture with clear separation of concerns
3. **Implements AI Concepts:** Rule-based system with explanations (simpler than ML but educationally sound)
4. **Addresses Real-World Problem:** Personal finance management is a common challenge
5. **Includes Best Practices:** Security, testing, documentation, error handling
6. **Has Clear Scope:** Focused on finance, not too broad, achievable in thesis timeline
7. **Shows Problem-Solving:** Expense classification, budget analysis, recommendation generation
8. **Emphasizes Ethics:** Transparency, disclaimers, user control

---

## References & Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- Material-UI Documentation: https://mui.com/
- MongoDB Documentation: https://docs.mongodb.com/
- Personal Finance Best Practices: Industry standard guidelines

---

**Project Status:** ✅ Ready for Deployment and Thesis Submission

**Created:** June 2, 2026
