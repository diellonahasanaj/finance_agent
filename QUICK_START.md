# Personal Finance Advisor Agent - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or Atlas)
- Git

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend_python
pip install -r requirements.txt
```

#### 2. Configure Environment Variables
Create a `.env` file in `backend_python/`:
```env
MONGO_URI=mongodb://localhost:27017/finance_advisor
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ALGORITHM=HS256
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

#### 3. Run the Backend
```bash
cd backend_python
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

#### 1. Install Node Dependencies
```bash
cd frontend
npm install
```

#### 2. Configure API Base URL
Edit `frontend/src/services/api.js`:
```javascript
const API = axios.create({
  baseURL: 'http://localhost:8000/api',
  // ...
});
```

#### 3. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

---

## 📚 API Documentation

### Authentication
```bash
# Register
POST /api/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure_password"
}

# Login
POST /api/auth/login
{
  "email": "john@example.com",
  "password": "secure_password"
}
```

### Expenses
```bash
# Add expense
POST /api/finance/expense
{
  "amount": 45.50,
  "category": "Food",
  "description": "Lunch at restaurant",
  "date": "2026-06-02"
}

# Get expenses
GET /api/finance/expense

# Get expenses by month
GET /api/finance/expense?month=2026-06

# Get expenses by category
GET /api/finance/expense?category=Food
```

### Budgets
```bash
# Create budget
POST /api/finance/budget
{
  "category": "Food",
  "limit": 500,
  "month": "2026-06"
}

# Get budgets
GET /api/finance/budget
```

### Financial Planning
```bash
# Calculate debt payoff plan
POST /api/planning/debt-repayment
{
  "monthly_payment": 1000,
  "strategy": "avalanche"
}

# Calculate savings goal
POST /api/planning/savings-goal
{
  "goal_amount": 10000,
  "current_savings": 2000,
  "monthly_contribution": 500
}

# Get financial health analysis
GET /api/planning/financial-health
```

### Alerts
```bash
# Get active alerts
GET /api/alerts

# Dismiss alert
POST /api/alerts/dismiss/alert_id_here

# Get alerts summary
GET /api/alerts/summary
```

### Chatbot
```bash
# Chat with advisor
POST /api/finance/ai-chat
{
  "message": "How much do I spend on food?"
}
```

---

## 🎮 Using the Application

### First Time Setup
1. Register a new account
2. Navigate to "Add Expense" and add your first expense
3. Go to "Set Budget" and create a budget
4. Check "Dashboard" to see your overview
5. Try asking the "Financial Advisor" questions

### Adding Expenses
1. Click "Add Expense" in sidebar
2. Enter amount, category, and date
3. (Optional) Add description and tags
4. Click "Add"

### Setting Budgets
1. Click "Set Budget" in sidebar
2. Select category and enter monthly limit
3. Click "Set Budget"
4. Budget alerts activate at 80% and 100%

### Using Financial Advisor
1. Click "Financial Advisor" in sidebar
2. Type your question naturally
3. Examples:
   - "How much do I spend on food?"
   - "What's my financial health?"
   - "Should I reduce entertainment spending?"
   - "Help me plan debt repayment"

### Checking Recommendations
1. Click "Recommendations" in sidebar
2. Review AI-generated recommendations
3. Each shows title, description, and reasoning
4. Follow suggested actions

### Viewing Analytics
1. Click "Analytics" in sidebar
2. See spending trends
3. View category breakdowns
4. Check budget status

### Adjusting Settings
1. Click "Settings" in sidebar
2. Toggle dark/light theme
3. Manage notification preferences
4. Change password or delete account

---

## 📊 Example Data

### Sample Expenses to Add
```json
[
  {
    "amount": 45.50,
    "category": "Food",
    "description": "Lunch",
    "date": "2026-06-01"
  },
  {
    "amount": 50,
    "category": "Transportation",
    "description": "Gas",
    "date": "2026-06-01"
  },
  {
    "amount": 25,
    "category": "Entertainment",
    "description": "Movie tickets",
    "date": "2026-06-02"
  },
  {
    "amount": 150,
    "category": "Housing",
    "description": "Partial rent",
    "date": "2026-06-02"
  },
  {
    "amount": 30,
    "category": "Utilities",
    "description": "Internet",
    "date": "2026-06-02"
  }
]
```

### Sample Budgets
```json
[
  {
    "category": "Food",
    "limit": 500,
    "month": "2026-06"
  },
  {
    "category": "Transportation",
    "limit": 200,
    "month": "2026-06"
  },
  {
    "category": "Entertainment",
    "limit": 100,
    "month": "2026-06"
  }
]
```

---

## 🔧 Troubleshooting

### Backend Won't Start
```bash
# Check if MongoDB is running
mongod

# Check port 8000 isn't in use
lsof -i :8000

# Reinstall dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Won't Start
```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Clear npm cache
npm cache clean --force
npm run dev
```

### API Connection Issues
- Check backend is running on `http://localhost:8000`
- Check `frontend/src/services/api.js` has correct baseURL
- Check CORS is enabled in backend
- Clear browser cache and cookies

### MongoDB Connection Issues
```bash
# Check MongoDB is running
mongosh

# Verify connection string in .env file
# Format: mongodb://username:password@host:port/database
```

---

## 🐛 Testing

### Test API Endpoints
```bash
# Using curl
curl -X POST http://localhost:8000/api/finance/ai-chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"How much do I spend?"}'

# Or use Postman/Insomnia
# 1. Create POST request to http://localhost:8000/api/finance/ai-chat
# 2. Add Authorization header with Bearer token
# 3. Send message in JSON body
```

### Test UI Components
1. Add expenses and verify they appear in expense table
2. Set budgets and verify alerts trigger at 80% and 100%
3. Toggle dark/light theme and verify changes persist
4. Test chatbot with various question types
5. Verify recommendations display correctly

---

## 📈 Performance Tips

### Backend Optimization
- Use MongoDB indexes on frequently queried fields
- Implement caching for recommendations (Redis)
- Use pagination for large result sets
- Compress API responses

### Frontend Optimization
- Lazy load pages
- Memoize expensive components
- Use virtual lists for long tables
- Compress images
- Enable gzip compression

---

## 🔒 Security Best Practices

1. **Never commit secrets** - Use .env files
2. **Validate all inputs** - Backend already does this
3. **Use HTTPS in production** - Configure SSL certificate
4. **Keep dependencies updated** - Run `npm audit` and `pip check`
5. **Set strong JWT secret** - Use random 32+ character string
6. **Enable CORS properly** - Only allow frontend URL
7. **Rate limit API endpoints** - Prevent abuse
8. **Sanitize user input** - Already handled in components

---

## 📦 Deployment

### Deploy Backend (Heroku Example)
```bash
# Create Procfile
echo "web: uvicorn app.core.app:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku login
heroku create your-app-name
git push heroku main
```

### Deploy Frontend (Vercel Example)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

---

## 📚 Documentation Files

- `IMPLEMENTATION_SUMMARY.md` - Complete transformation summary
- `FEATURE_VERIFICATION_CHECKLIST.md` - Feature checklist
- `README.md` - Project overview
- `THESIS_PROJECT_DOCUMENTATION.md` - Original thesis documentation

---

## 💡 Tips & Tricks

### For Developers
1. Use VS Code extensions: Python, Prettier, ESLint
2. Use browser DevTools for frontend debugging
3. Use MongoDB Compass for database visualization
4. Use Postman for API testing
5. Enable debug logging in FastAPI

### For Users
1. Add regular expenses to get better recommendations
2. Set realistic budgets to track progress
3. Check the Financial Advisor frequently for new insights
4. Review recommendations weekly
5. Export data regularly for backup

---

## 🎓 Learning Path

1. **Beginner**: Add expenses, create budgets, view dashboard
2. **Intermediate**: Use Financial Advisor, review recommendations
3. **Advanced**: Use debt planning, savings goals, financial health analysis
4. **Expert**: Interpret confidence scores, understand algorithms, modify settings

---

## 📞 Support Resources

- Check Transparency page for system information
- Review tips in Financial Advisor page
- Check Settings for preferences
- Review example conversations in this guide
- Check GitHub issues (if applicable)

---

**Last Updated**: June 2, 2026
**Version**: 2.0
**Status**: Production Ready ✅
