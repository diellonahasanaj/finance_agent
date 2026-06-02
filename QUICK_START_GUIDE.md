# Quick Start Guide - Personal Finance Advisor Agent

## 📋 Prerequisites

- Python 3.13+
- Node.js 16+
- npm 8+
- MongoDB (local or Atlas)
- Git

## 🚀 Quick Setup (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend_python

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Backend is now running on: **http://localhost:8000**

### 2. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected output:**
```
VITE v7.3.1  ready in 234 ms

➜  Local:   http://localhost:5173/
```

Frontend is now running on: **http://localhost:5173**

## ✅ Initial Tests

### Test 1: Register & Login
1. Open http://localhost:5173
2. Click "Register"
3. Enter test credentials:
   - Name: Test User
   - Email: test@example.com
   - Password: Test123!
4. Click "Register"
5. Login with your credentials

### Test 2: Add Expense
1. Click "Add Expense" in sidebar
2. Fill form:
   - Title: "Coffee at Starbucks"
   - Amount: 5.50
   - Description: "Morning coffee"
   - Category: Leave blank (auto-classify)
3. Submit
4. Verify expense appears on Dashboard

### Test 3: Set Budget
1. Click "Set Budget" in sidebar
2. Create budget:
   - Category: "Food"
   - Limit: 500
   - Month: Current month
3. Submit
4. Add more food expenses to test alerts

### Test 4: View Recommendations
1. Click "AI Recommendations" in sidebar
2. Verify recommendations generated
3. Expand cards to see details
4. Check action steps and explanations

### Test 5: View Analytics
1. Click "Analytics" in sidebar
2. See charts loading
3. Verify category breakdown pie chart
4. Check monthly trend line chart

### Test 6: View How It Works
1. Click "How It Works" in sidebar
2. Read process explanation
3. Review ethical guidelines
4. Check FAQ section

## 📊 Test Data

### Create Sample Data
```python
# Add to backend for testing
expenses = [
    {"title": "Grocery Store", "amount": 150, "category": "Food"},
    {"title": "Gas Station", "amount": 50, "category": "Transportation"},
    {"title": "Netflix", "amount": 12.99, "category": "Entertainment"},
    {"title": "Gym Membership", "amount": 30, "category": "Health"},
    {"title": "Book", "amount": 20, "category": "Education"},
]

budgets = [
    {"category": "Food", "limit": 400, "month": "2026-06"},
    {"category": "Transportation", "limit": 200, "month": "2026-06"},
    {"category": "Entertainment", "limit": 100, "month": "2026-06"},
]
```

## 🔍 Key Endpoints to Test

### API Testing (using curl or Postman)

#### Get Recommendations
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/recommendations/recommendations
```

#### Classify Expense
```bash
curl -X POST http://localhost:8000/recommendations/classify-expense \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Starbucks Coffee",
    "description": "Morning coffee at Starbucks",
    "current_category": ""
  }'
```

#### Get How It Works
```bash
curl http://localhost:8000/recommendations/how-it-works \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Troubleshooting

### Backend Issues

**Error: "Address already in use"**
```bash
# The port 8000 is already in use
# Kill process or use different port
python run.py --port 8001
```

**Error: "ModuleNotFoundError"**
```bash
# Dependencies not installed
pip install -r requirements.txt
```

**Error: "Connection refused to MongoDB"**
```bash
# Ensure MongoDB is running
# Update MONGO_URI in app/core/config.py
```

### Frontend Issues

**Error: "npm command not found"**
```bash
# Install Node.js from https://nodejs.org/
```

**Error: "Port 5173 already in use"**
```bash
# Use different port
npm run dev -- --port 5174
```

**Error: "CORS error"**
```bash
# Backend CORS settings allow localhost
# Check app/core/app.py for CORS configuration
```

## 📱 Project Structure Quick Reference

```
PersonalFinanceAgent/
├── backend_python/
│   ├── app/
│   │   ├── api/                      # API endpoints
│   │   ├── services/
│   │   │   ├── expense_classifier.py        # Classification
│   │   │   ├── recommendation_engine_v2.py  # Recommendations
│   │   │   └── budget_analysis_service.py   # Budget analysis
│   │   ├── models/                   # Data models
│   │   └── core/                     # App configuration
│   └── run.py                        # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Recommendations.tsx   # Recommendations
│   │   │   ├── Analytics.tsx         # Analytics
│   │   │   ├── Transparency.tsx      # How it works
│   │   │   └── Dashboard.tsx         # Dashboard
│   │   └── components/               # UI Components
│   └── package.json
│
├── THESIS_PROJECT_DOCUMENTATION.md   # Full documentation
└── TRANSFORMATION_SUMMARY.md         # Changes summary
```

## 🎓 Features to Demonstrate for Thesis

### Core Features
✅ Expense classification using keyword matching
✅ Rule-based recommendation engine with explanations
✅ Budget management with real-time alerts
✅ Financial analytics with charts
✅ Ethical transparency layer

### Technical Features
✅ Modern API with FastAPI
✅ Async database operations
✅ JWT authentication
✅ Responsive React frontend
✅ Material-UI components
✅ Chart visualizations

### UI Features
✅ Dashboard with metrics
✅ Recommendations page with expandable cards
✅ Analytics with multiple charts
✅ How It Works page with FAQ
✅ Loading and error states
✅ Responsive mobile design

## 📝 Example Workflows

### Workflow 1: Detect Budget Overrun
1. Set Food budget: $400
2. Add expenses: $150, $180, $100 (total: $430)
3. View Dashboard → See budget warning
4. View Recommendations → Get alert to reduce food spending
5. See action steps to prevent future overruns

### Workflow 2: Get Savings Recommendation
1. Add income: $3000
2. Add expenses: $2400 total (savings: $600 = 20%)
3. View Recommendations → No savings recommendation (target met)
4. Add more expenses: $2700 total (savings: $300 = 10%)
5. View Recommendations → Get "Increase Savings" recommendation

### Workflow 3: Analyze Spending Patterns
1. Add multiple expenses across categories
2. View Analytics page
3. See pie chart of spending breakdown
4. Check which categories need attention
5. Use recommendations to optimize spending

## 🔐 Security Notes

- Never commit `.env` with credentials
- Use environment variables for sensitive data
- Passwords are hashed with bcrypt
- JWT tokens expire after configured time
- Frontend stores token in localStorage (consider secure storage)

## 📈 Monitoring & Logging

### Backend Logs
Check console output for:
- Database connections
- API requests
- Recommendation generation
- Error messages

### Frontend Logs
Open browser console (F12) to see:
- API request/response
- React warnings
- Component renders

## 🚢 Deployment Tips

### For Production

```bash
# Backend
gunicorn app.core.app:create_app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ folder with web server
```

### Environment Variables
```bash
# .env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
JWT_SECRET=your_secret_key_here
API_URL=https://api.example.com
```

## 💡 Tips & Tricks

### See All Available Routes
```bash
# Backend automatically generates API docs
# Visit http://localhost:8000/docs (Swagger UI)
# Visit http://localhost:8000/redoc (ReDoc)
```

### Debug Mode
```python
# In app/core/config.py
DEBUG = True  # Gives more verbose error messages
```

### Clear Test Data
```bash
# Reset database (delete all data)
python reset_password.py  # Uses existing test reset script
```

## ❓ FAQ

**Q: Can I use this without MongoDB?**
A: Currently MongoDB is required. To use different DB, modify services/finance_service.py

**Q: How do I add more categories?**
A: Edit CATEGORY_KEYWORDS in services/expense_classifier.py

**Q: Can I customize recommendations?**
A: Yes! Edit rules in services/recommendation_engine_v2.py

**Q: Is there a way to export data?**
A: You can implement export via new API endpoint (great enhancement idea!)

## 🎯 Next Steps

1. ✅ Setup backend and frontend
2. ✅ Test all features
3. ✅ Review code quality
4. ✅ Test with sample data
5. ✅ Review documentation
6. 📝 Prepare thesis presentation
7. 🚀 Deploy for demonstration

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review THESIS_PROJECT_DOCUMENTATION.md
3. Check API documentation at /docs
4. Review browser console for frontend errors

---

**Ready to start? Run these commands:**

```bash
# Terminal 1: Backend
cd backend_python && python run.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Open: http://localhost:5173
```

**Success!** 🎉 Your AI Financial Advisor is running!
