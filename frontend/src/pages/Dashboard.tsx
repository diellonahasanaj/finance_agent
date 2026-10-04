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
  CircularProgress,
  Alert,
  Chip,
} from "@mui/material";
import {
  AccountBalanceWallet,
  TrendingUp,
  TrendingDown,
  Savings,
  Lightbulb,
  Refresh,
  Add,
  Warning,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

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
  balance: number;
  total_debts: number;
  budgets: Array<{
    category: string;
    limit: number;
    spent: number;
    remaining: number;
    percentage: number;
  }>;
  alerts: Array<{
    type: string;
    message: string;
    reason: string;
    impact: string;
  }>;
  recommendations: Array<{
    title: string;
    description: string;
    priority: string;
    reasoning: string;
    category: string;
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
  savings_rate: number;
  savings_goal_progress: number;
}

function Dashboard() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [month, setMonth] = useState(() => new Date().toISOString().slice(0, 7));
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, [month]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await API.get("/finance/dashboard", { params: { month } });
      setDashboardData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);

  const stats: StatCard[] = dashboardData
    ? [
        {
          title: "Net Income",
          value: formatCurrency(dashboardData.net_income),
          change: dashboardData.savings_rate,
          icon: <AccountBalanceWallet />,
          color:
            dashboardData.net_income >= 0
              ? theme.palette.success.main
              : theme.palette.error.main,
        },
        {
          title: "Total Income",
          value: formatCurrency(dashboardData.total_income),
          change: dashboardData.savings_rate,
          icon: <TrendingUp />,
          color: theme.palette.success.main,
        },
        {
          title: "Total Expenses",
          value: formatCurrency(dashboardData.total_expenses),
          change: -dashboardData.savings_rate,
          icon: <TrendingDown />,
          color: theme.palette.error.main,
        },
        {
          title: "Total Debts",
          value: formatCurrency(dashboardData.total_debts),
          change: 0,
          icon: <Savings />,
          color: theme.palette.warning.main,
        },
      ]
    : [];

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, minHeight: '100vh' }}>
      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
          <CircularProgress size={60} />
        </Box>
      ) : error ? (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
          <Typography variant="h6" color="error">{error}</Typography>
        </Box>
      ) : (
        <>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4, flexWrap: "wrap", gap: 2 }}>
            <Box>
              <Typography variant="h3" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
                Financial Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Track your financial health and receive intelligent guidance
              </Typography>
            </Box>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <Paper sx={{ p: 1, display: "flex", alignItems: "center", gap: 1 }}>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  Month:
                </Typography>
                <TextField
                  type="month"
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  size="small"
                  sx={{ width: 150 }}
                />
              </Paper>
              <Tooltip title="Refresh Data">
                <IconButton onClick={fetchDashboardData}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {dashboardData?.alerts && dashboardData.alerts.length > 0 && (
            <Box sx={{ mb: 3, display: "flex", flexDirection: "column", gap: 1 }}>
              {dashboardData.alerts.map((alert, index) => (
                <Alert
                  key={index}
                  severity={alert.type === "error" ? "error" : alert.type === "warning" ? "warning" : "info"}
                  icon={<Warning />}
                >
                  <strong>{alert.message}</strong> — {alert.reason}. {alert.impact}
                </Alert>
              ))}
            </Box>
          )}

          <Grid container spacing={3} sx={{ mb: 4 }}>
            {stats.map((stat, index) => (
              <Grid item key={stat.title} xs={12} sm={6} lg={3}>
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}>
                  <Card sx={{ height: "100%", borderRadius: 3 }}>
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                        <Avatar sx={{ backgroundColor: alpha(stat.color, 0.1), color: stat.color, width: 48, height: 48 }}>
                          {stat.icon}
                        </Avatar>
                        {stat.title === "Net Income" && (
                          <Typography variant="caption" color={stat.change >= 0 ? "success.main" : "error.main"} sx={{ fontWeight: 600 }}>
                            {stat.change.toFixed(1)}% savings rate
                          </Typography>
                        )}
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>{stat.value}</Typography>
                      <Typography variant="body2" color="text.secondary">{stat.title}</Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>

          {dashboardData?.budgets && dashboardData.budgets.length > 0 && (
            <Card sx={{ mb: 4, borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Budget Status</Typography>
                <Grid container spacing={2}>
                  {dashboardData.budgets.map((budget) => (
                    <Grid item xs={12} sm={6} lg={4} key={budget.category}>
                      <Box sx={{ mb: 1, display: "flex", justifyContent: "space-between" }}>
                        <Typography variant="body2">{budget.category}</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {formatCurrency(budget.spent)} / {formatCurrency(budget.limit)}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(budget.percentage, 100)}
                        color={budget.percentage > 100 ? "error" : budget.percentage >= 80 ? "warning" : "primary"}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} lg={6}>
              <Card sx={{ height: "100%", borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Recent Transactions</Typography>
                    <IconButton size="small" onClick={() => navigate("/add-transaction")}>
                      <Add />
                    </IconButton>
                  </Box>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    {dashboardData?.recent_transactions?.map((transaction) => (
                      <Box
                        key={transaction._id}
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          p: 2,
                          borderRadius: 2,
                          backgroundColor: alpha(theme.palette.background.default, 0.5),
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {transaction.description || transaction.category || transaction.source || "Transaction"}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {transaction.category || transaction.source || "General"} • {transaction.date}
                          </Typography>
                        </Box>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 600,
                            color: transaction.source ? theme.palette.success.main : theme.palette.error.main,
                          }}
                        >
                          {transaction.source ? "+" : "-"}
                          {formatCurrency(transaction.amount)}
                        </Typography>
                      </Box>
                    ))}
                    {!dashboardData?.recent_transactions?.length && (
                      <Typography variant="body2" color="text.secondary">
                        No transactions yet. Start by adding your income and expenses.
                      </Typography>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} lg={6}>
              <Card sx={{ height: "100%", borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                    <Avatar sx={{ backgroundColor: alpha(theme.palette.secondary.main, 0.1), color: theme.palette.secondary.main, mr: 2 }}>
                      <Lightbulb />
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>Recommendations</Typography>
                  </Box>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    {dashboardData?.recommendations?.slice(0, 3).map((rec, index) => (
                      <Paper key={index} sx={{ p: 2, borderRadius: 2 }} elevation={0}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>{rec.title}</Typography>
                          <Chip label={rec.priority} size="small" color={rec.priority === "high" ? "error" : "warning"} />
                        </Box>
                        <Typography variant="body2" color="text.secondary">{rec.reasoning}</Typography>
                      </Paper>
                    ))}
                    {!dashboardData?.recommendations?.length && (
                      <Typography variant="body2" color="text.secondary">
                        Add income, expenses, and budgets to receive personalized recommendations.
                      </Typography>
                    )}
                  </Box>
                  <Box sx={{ mt: 3, p: 2, borderRadius: 2, backgroundColor: alpha(theme.palette.success.main, 0.05) }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Savings Goal Progress (20% target)
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={dashboardData?.savings_goal_progress || 0}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                      {(dashboardData?.savings_goal_progress || 0).toFixed(0)}% of monthly savings goal achieved
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}

export default Dashboard;
