import { useState, useEffect, useRef } from "react";
import {
  Box,
  Typography,
  Card,      
  CardContent,
  Grid,
  Button,
  TextField,
  Paper,
  List,
  ListItem,
  ListItemText,
  Alert,
  Chip,
  CircularProgress,
  useTheme,
  IconButton
} from '@mui/material';
import {
  AttachMoney,
  AccountBalanceWallet,
  ShoppingCart,
  Lightbulb,
  Send,
  Refresh
} from '@mui/icons-material';
// @ts-ignore
import API from '../services/api';

interface FinancialData {
  incomes: any[];
  expenses: any[];
  budgets: any[];
  debts: any[];
}

interface Analysis {
  totalIncome: number;
  totalExpenses: number;
  balance: number;
  budgetStatus: any[];
  alerts: Alert[];
  recommendations: Recommendation[];
}

interface Alert {
  type: 'warning' | 'error' | 'info';
  message: string;
  reason: string;
  impact: string;
  data: any;
}

interface Recommendation {
  category: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  potentialSavings: number;
  reasoning: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  data?: any;
}

function Reports() {
  const theme = useTheme();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchFinancialData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchFinancialData = async () => {
    try {
      setLoading(true);
      const [incomesRes, expensesRes, budgetsRes] = await Promise.all([
        API.get('/finance/income'),
        API.get('/finance/expense'),
        API.get('/finance/budget')
      ]);

      const data = {
        incomes: incomesRes.data,
        expenses: expensesRes.data,
        budgets: budgetsRes.data,
        debts: []
      };

      performAnalysis(data);
    } catch (error: any) {
      console.error('Failed to fetch financial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const performAnalysis = (data: FinancialData) => {
    const totalIncome = data.incomes.reduce((sum, inc) => sum + inc.amount, 0);
    const totalExpenses = data.expenses.reduce((sum, exp) => sum + exp.amount, 0);
    const balance = totalIncome - totalExpenses;

    // Generate alerts
    const alerts: Alert[] = [];
    
    if (balance < 0) {
      alerts.push({
        type: 'error',
        message: 'Monthly balance is negative',
        reason: `Total expenses ($${totalExpenses.toFixed(2)}) exceed total income ($${totalIncome.toFixed(2)})`,
        impact: 'You are spending more than you earn this month',
        data: { balance, totalIncome, totalExpenses }
      });
    }

    // Check budget status
    const budgetStatus = data.budgets.map(budget => {
      const categoryExpenses = data.expenses
        .filter(exp => exp.category === budget.category)
        .reduce((sum, exp) => sum + exp.amount, 0);
      
      const percentageUsed = (categoryExpenses / budget.limit) * 100;
      
      if (percentageUsed > 100) {
        alerts.push({
          type: 'warning',
          message: `${budget.category} budget exceeded`,
          reason: `Spent $${categoryExpenses.toFixed(2)} of $${budget.limit.toFixed(2)} budget`,
          impact: `Over budget by $${(categoryExpenses - budget.limit).toFixed(2)}`,
          data: { category: budget.category, spent: categoryExpenses, limit: budget.limit }
        });
      } else if (percentageUsed > 80) {
        alerts.push({
          type: 'info',
          message: `${budget.category} budget nearly exceeded`,
          reason: `Used ${percentageUsed.toFixed(1)}% of budget`,
          impact: `Only $${(budget.limit - categoryExpenses).toFixed(2)} remaining`,
          data: { category: budget.category, percentageUsed, remaining: budget.limit - categoryExpenses }
        });
      }

      return {
        category: budget.category,
        limit: budget.limit,
        spent: categoryExpenses,
        remaining: budget.limit - categoryExpenses,
        percentageUsed
      };
    });

    // Generate recommendations
    const recommendations: Recommendation[] = [];
    
    // Analyze spending by category
    const spendingByCategory: { [key: string]: number } = data.expenses.reduce((acc, exp) => {
      const amount = typeof exp.amount === 'number' ? exp.amount : parseFloat(exp.amount) || 0;
      acc[exp.category] = (acc[exp.category] || 0) + amount;
      return acc;
    }, {});

    Object.entries(spendingByCategory).forEach(([category, amount]) => {
      const budget = data.budgets.find(b => b.category === category);
      if (budget && amount > budget.limit) {
        const budgetLimit = typeof budget.limit === 'number' ? budget.limit : parseFloat(budget.limit) || 0;
        recommendations.push({
          category,
          title: `Reduce ${category} spending`,
          description: `Consider cutting back on ${category} expenses by $${(amount - budgetLimit).toFixed(2)}`,
          priority: 'high' as const,
          potentialSavings: amount - budgetLimit,
          reasoning: `You spent $${amount.toFixed(2)} on ${category}, which is $${(amount - budgetLimit).toFixed(2)} over your budget of $${budgetLimit.toFixed(2)}`
        });
      }
    });

    if (balance > 0) {
      recommendations.push({
        category: 'Savings',
        title: 'Increase savings',
        description: `You have a surplus of $${balance.toFixed(2)}. Consider adding this to your emergency fund or investments.`,
        priority: 'medium' as const,
        potentialSavings: balance,
        reasoning: `Your positive balance of $${balance.toFixed(2)} can be used to build financial security`
      });
    }

    setAnalysis({
      totalIncome,
      totalExpenses,
      balance,
      budgetStatus,
      alerts,
      recommendations
    });
  };

  const generateAIResponse = async (userMessage: string) => {
    try {
      const response = await API.post('/finance/ai-chat', { message: userMessage });
      return {
        content: response.data.response,
        data: response.data.data
      };
    } catch (error: any) {
      console.error('AI Chat Error:', error);
      return {
        content: 'Sorry, I encountered an error. Please try again.',
        data: null
      };
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setChatLoading(true);

    try {
      const aiResponse = await generateAIResponse(inputMessage);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: aiResponse.content,
        timestamp: new Date(),
        data: aiResponse.data
      };

      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 1400, mx: 'auto' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Financial Reports & AI Assistant
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={fetchFinancialData}
          variant="outlined"
        >
          Refresh Data
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Financial Summary */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            {/* Summary Cards */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AttachMoney color="success" />
                    <Typography variant="h6" sx={{ ml: 1 }}>Income</Typography>
                  </Box>
                  <Typography variant="h4" color="success.main">
                    ${analysis?.totalIncome.toFixed(2) || '0.00'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <ShoppingCart color="error" />
                    <Typography variant="h6" sx={{ ml: 1 }}>Expenses</Typography>
                  </Box>
                  <Typography variant="h4" color="error.main">
                    ${analysis?.totalExpenses.toFixed(2) || '0.00'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AccountBalanceWallet color="primary" />
                    <Typography variant="h6" sx={{ ml: 1 }}>Balance</Typography>
                  </Box>
                  <Typography 
                    variant="h4" 
                    color={analysis?.balance !== undefined && analysis.balance >= 0 ? 'success.main' : 'error.main'}
                  >
                    ${analysis?.balance?.toFixed(2) || '0.00'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Lightbulb color="warning" />
                    <Typography variant="h6" sx={{ ml: 1 }}>Alerts</Typography>
                  </Box>
                  <Typography variant="h4" color="warning.main">
                    {analysis?.alerts.length || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Budget Status */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Budget Status</Typography>
                  {analysis?.budgetStatus.length ? (
                    <List>
                      {analysis.budgetStatus.map((budget, index) => (
                        <ListItem key={index} sx={{ borderLeft: `4px solid ${
                          budget.percentageUsed > 100 ? theme.palette.error.main :
                          budget.percentageUsed > 80 ? theme.palette.warning.main :
                          theme.palette.success.main
                        }`, mb: 1 }}>
                          <ListItemText
                            primary={budget.category}
                            secondary={
                              <Box>
                                <Typography variant="body2">
                                  ${budget.spent.toFixed(2)} / ${budget.limit.toFixed(2)} 
                                  ({budget.percentageUsed.toFixed(1)}%)
                                </Typography>
                                <Box sx={{ width: '100%', backgroundColor: 'grey.200', borderRadius: 1, mt: 1 }}>
                                  <Box 
                                    sx={{ 
                                      width: `${Math.min(budget.percentageUsed, 100)}%`,
                                      height: 8,
                                      backgroundColor: budget.percentageUsed > 100 ? 'error.main' :
                                                       budget.percentageUsed > 80 ? 'warning.main' :
                                                       'success.main',
                                      borderRadius: 1
                                    }}
                                  />
                                </Box>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No budgets set yet
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Alerts */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Alerts & Warnings</Typography>
                  {analysis?.alerts.length ? (
                    <List>
                      {analysis.alerts.map((alert, index) => (
                        <Alert 
                          key={index} 
                          severity={alert.type}
                          sx={{ mb: 2 }}
                        >
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {alert.message}
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            <strong>Why:</strong> {alert.reason}
                          </Typography>
                          <Typography variant="body2">
                            <strong>Impact:</strong> {alert.impact}
                          </Typography>
                        </Alert>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No alerts at this time
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Recommendations */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>AI Recommendations</Typography>
                  {analysis?.recommendations.length ? (
                    <List>
                      {analysis.recommendations.map((rec, index) => (
                        <Card key={index} sx={{ mb: 2, border: `1px solid ${
                          rec.priority === 'high' ? theme.palette.error.main :
                          rec.priority === 'medium' ? theme.palette.warning.main :
                          theme.palette.success.main
                        }` }}>
                          <CardContent sx={{ pb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                {rec.title}
                              </Typography>
                              <Chip 
                                label={rec.priority.toUpperCase()} 
                                color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'success'}
                                size="small"
                              />
                            </Box>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              {rec.description}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              <strong>Reasoning:</strong> {rec.reasoning}
                            </Typography>
                            {rec.potentialSavings > 0 && (
                              <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                                <strong>Potential savings:</strong> ${rec.potentialSavings.toFixed(2)}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No recommendations at this time
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* AI Chat Assistant */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2 }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <Lightbulb sx={{ mr: 1, color: theme.palette.primary.main }} />
                AI Financial Assistant
              </Typography>
              
              <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2, border: `1px solid ${theme.palette.divider}`, borderRadius: 2, p: 2 }}>
                {chatMessages.length === 0 ? (
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                      Ask me about your budget, spending, savings, or financial goals!
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Try asking:
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {[
                          "How much do I spend on food?",
                          "What's my current balance?",
                          "Show me my spending breakdown",
                          "Compare income vs expenses",
                          "Help me reduce my expenses",
                          "Calculate my savings potential",
                          "Am I overspending?",
                          "Explain my financial situation"
                        ].map((prompt, index) => (
                          <Box
                            key={index}
                            sx={{
                              p: 1,
                              backgroundColor: theme.palette.grey[50],
                              borderRadius: 1,
                              cursor: 'pointer',
                              '&:hover': {
                                backgroundColor: theme.palette.grey[100]
                              }
                            }}
                            onClick={() => setInputMessage(prompt)}
                          >
                            <Typography variant="body2" color="primary.main">
                              💬 {prompt}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  </Box>
                ) : (
                  chatMessages.map((message) => (
                    <Box
                      key={message.id}
                      sx={{
                        mb: 2,
                        display: 'flex',
                        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
                      }}
                    >
                      <Paper
                        sx={{
                          p: 2,
                          maxWidth: '80%',
                          backgroundColor: message.type === 'user' ? theme.palette.primary.main : theme.palette.grey[100],
                          color: message.type === 'user' ? 'white' : 'text.primary',
                          whiteSpace: 'pre-line',
                          wordBreak: 'break-word'
                        }}
                      >
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.5 }}>
                          {message.content}
                        </Typography>
                      </Paper>
                    </Box>
                  ))
                )}
                {chatLoading && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                    <Paper sx={{ p: 2, backgroundColor: theme.palette.grey[100] }}>
                      <CircularProgress size={20} />
                    </Paper>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Ask about your finances..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={chatLoading}
                />
                <IconButton 
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || chatLoading}
                  color="primary"
                >
                  <Send />
                </IconButton>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Reports;
