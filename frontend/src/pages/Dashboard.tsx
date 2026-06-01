

import { useState, useEffect } from "react";
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Grid, 
  Card, 
  CardContent, 
  Avatar,
  LinearProgress,
  useTheme,
  alpha,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { 
  AccountBalanceWallet,
  TrendingUp,
  TrendingDown,
  Savings,
  Lightbulb,
  Refresh,
  Add
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
// @ts-ignore
import API from '../services/api';

interface StatCard {
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: string;
}

interface DashboardData {
  total_income: number;
  total_expenses: number;
  net_income: number;
  total_debts: number;
  budgets: Array<{
    category: string;
    limit: number;
    spent: number;
    remaining: number;
    percentage: number;
  }>;
  recent_transactions: Array<{
    _id: string;
    amount: number;
    category?: string;
    source?: string;
    date: string;
    description?: string;
  }>;
  income_count: number;
  expense_count: number;
  budget_count: number;
  debt_count: number;
}

function Dashboard() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [month, setMonth] = useState(() => {
    const d = new Date();
    return d.toISOString().slice(0, 7);
  });
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Refresh data when component gains focus (user navigates back)
  useEffect(() => {
    const handleFocus = () => {
      fetchDashboardData();
    };

    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await API.get("/finance/dashboard");
      setDashboardData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const stats: StatCard[] = dashboardData ? [
    {
      title: 'Net Income',
      value: formatCurrency(dashboardData.net_income),
      change: dashboardData.total_income > 0 ? ((dashboardData.net_income / dashboardData.total_income) * 100) : 0,
      icon: <AccountBalanceWallet />,
      color: dashboardData.net_income >= 0 ? theme.palette.success.main : theme.palette.error.main
    },
    {
      title: 'Total Income',
      value: formatCurrency(dashboardData.total_income),
      change: 8.2,
      icon: <TrendingUp />,
      color: theme.palette.success.main
    },
    {
      title: 'Total Expenses',
      value: formatCurrency(dashboardData.total_expenses),
      change: -5.3,
      icon: <TrendingDown />,
      color: theme.palette.error.main
    },
    {
      title: 'Total Debts',
      value: formatCurrency(dashboardData.total_debts),
      change: -2.1,
      icon: <Savings />,
      color: theme.palette.warning.main
    }
  ] : [];

  const aiInsights = dashboardData ? [
    `You have ${dashboardData.income_count} income records and ${dashboardData.expense_count} expense records.`,
    `Your net income is ${dashboardData.net_income >= 0 ? 'positive' : 'negative'}.`,
    `You have ${dashboardData.budget_count} active budgets to track.`,
  ] : [];

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress size={60} />
        </Box>
      ) : error ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <Typography variant="h6" color="error">{error}</Typography>
        </Box>
      ) : (
        <>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 4,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <Box>
          <Typography 
            variant="h3" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              mb: 1
            }}
          >
            Financial Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track your financial health and make informed decisions
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Paper sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
              Month:
            </Typography>
            <TextField
              type="month"
              value={month}
              onChange={e => setMonth(e.target.value)}
              size="small"
              sx={{ 
                width: 150,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />
          </Paper>
          
          <Tooltip title="Refresh Data">
            <IconButton 
              onClick={fetchDashboardData}
              sx={{ 
                backgroundColor: alpha(theme.palette.primary.main, 0.1),
                '&:hover': {
                  backgroundColor: alpha(theme.palette.primary.main, 0.2),
                }
              }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item key={stat.title} xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card 
                sx={{ 
                  height: '100%',
                  borderRadius: 3,
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        backgroundColor: alpha(stat.color, 0.1),
                        color: stat.color,
                        width: 48,
                        height: 48
                      }}
                    >
                      {stat.icon}
                    </Avatar>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography 
                        variant="caption" 
                        color={stat.change > 0 ? 'success.main' : 'error.main'}
                        sx={{ fontWeight: 600 }}
                      >
                        {stat.change > 0 ? '+' : ''}{stat.change}%
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Expenses */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Recent Expenses
                  </Typography>
                  <IconButton 
                    size="small"
                    onClick={() => navigate('/add-transaction')}
                    sx={{ 
                      backgroundColor: alpha(theme.palette.primary.main, 0.1),
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.2),
                      }
                    }}
                  >
                    <Add />
                  </IconButton>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {dashboardData?.recent_transactions?.slice(0, 5).map((transaction, index) => (
                    <motion.div
                      key={transaction._id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.05 }}
                    >
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          p: 2,
                          borderRadius: 2,
                          backgroundColor: alpha(theme.palette.background.default, 0.5),
                          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: alpha(theme.palette.primary.main, 0.04),
                          }
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {transaction.description || transaction.category || transaction.source || 'Transaction'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {transaction.category || 'General'} • {transaction.date}
                          </Typography>
                        </Box>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: 600, 
                            color: transaction.category ? theme.palette.error.main : theme.palette.success.main 
                          }}
                        >
                          {transaction.category ? '-' : '+'}{formatCurrency(transaction.amount)}
                        </Typography>
                      </Box>
                    </motion.div>
                  ))}
                  {!dashboardData?.recent_transactions?.length && (
                    <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                      No transactions yet. Start by adding your income and expenses.
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* AI Insights */}
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Avatar 
                    sx={{ 
                      backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                      color: theme.palette.secondary.main,
                      mr: 2
                    }}
                  >
                    <Lightbulb />
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    AI Financial Insights
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {aiInsights.map((insight, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                    >
                      <Paper 
                        sx={{ 
                          p: 2,
                          borderRadius: 2,
                          backgroundColor: alpha(theme.palette.info.main, 0.05),
                          border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
                          borderLeft: `3px solid ${theme.palette.info.main}`
                        }}
                        elevation={0}
                      >
                        <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                          {insight}
                        </Typography>
                      </Paper>
                    </motion.div>
                  ))}
                </Box>
                
                <Box sx={{ mt: 3, p: 2, borderRadius: 2, backgroundColor: alpha(theme.palette.success.main, 0.05) }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    🎯 Monthly Goal Progress
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={75}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: alpha(theme.palette.divider, 0.2),
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: theme.palette.success.main,
                        borderRadius: 4,
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    75% of savings goal achieved
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
        </>
      )}
    </Box>
  );
}

export default Dashboard;
