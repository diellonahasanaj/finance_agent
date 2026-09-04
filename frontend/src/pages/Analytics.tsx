import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  useTheme,
  alpha,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Refresh, TrendingUp, TrendingDown } from "@mui/icons-material";
import API from "../services/api";

interface CategoryData {
  category: string;
  amount: number;
}

interface TrendData {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

interface AnalyticsData {
  categoryBreakdown: CategoryData[];
  monthlyTrends: TrendData[];
  budgetStatus: {
    total_budget: number;
    total_spent: number;
    percentage: number;
  };
  savingsRate: number;
}

const COLORS = [
  "#ff7300", "#00d084", "#2196f3", "#ff6b6b",
  "#ffd666", "#95de64", "#5cdbd3", "#9254de",
];

function AnalyticsPage() {
  const theme = useTheme();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await API.get("/finance/analytics", { params: { months: 6 } });
      setData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount);

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4, flexWrap: "wrap", gap: 2 }}>
        <Box>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
            Financial Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real spending patterns and trends from your transaction data
          </Typography>
        </Box>
        <Tooltip title="Refresh Analytics">
          <IconButton onClick={fetchAnalyticsData} disabled={loading}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
          <CircularProgress size={60} />
        </Box>
      )}

      {error && !loading && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {!loading && data && (
        <>
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, borderRadius: 2, background: alpha(theme.palette.success.main, 0.08) }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TrendingUp sx={{ color: theme.palette.success.main }} />
                  <Box>
                    <Typography variant="body2" color="text.secondary">Savings Rate</Typography>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: theme.palette.success.main }}>
                      {data.savingsRate.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, borderRadius: 2, background: alpha(theme.palette.warning.main, 0.08) }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TrendingDown sx={{ color: theme.palette.warning.main }} />
                  <Box>
                    <Typography variant="body2" color="text.secondary">Budget Usage</Typography>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: theme.palette.warning.main }}>
                      {data.budgetStatus.percentage.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card sx={{ height: "100%", borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Spending by Category</Typography>
                  {data.categoryBreakdown.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={data.categoryBreakdown}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ category, percent }) => `${category}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          dataKey="amount"
                        >
                          {data.categoryBreakdown.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <ChartTooltip formatter={(value) => formatCurrency(Number(value))} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography color="text.secondary">No spending data available</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card sx={{ height: "100%", borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Category Breakdown</Typography>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    {data.categoryBreakdown.map((category, index) => {
                      const total = data.categoryBreakdown.reduce((sum, c) => sum + c.amount, 0);
                      const percentage = total > 0 ? ((category.amount / total) * 100).toFixed(1) : "0";
                      return (
                        <Box key={category.category}>
                          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.5 }}>
                            <Typography variant="body2">{category.category}</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {formatCurrency(category.amount)} ({percentage}%)
                            </Typography>
                          </Box>
                          <Box sx={{ height: 6, borderRadius: 3, backgroundColor: alpha(theme.palette.divider, 0.2) }}>
                            <Box
                              sx={{
                                height: "100%",
                                width: `${percentage}%`,
                                backgroundColor: COLORS[index % COLORS.length],
                                borderRadius: 3,
                              }}
                            />
                          </Box>
                        </Box>
                      );
                    })}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Monthly Trends</Typography>
              {data.monthlyTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.monthlyTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <ChartTooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Legend />
                    <Line type="monotone" dataKey="income" stroke="#00d084" strokeWidth={2} name="Income" />
                    <Line type="monotone" dataKey="expenses" stroke="#ff7300" strokeWidth={2} name="Expenses" />
                    <Line type="monotone" dataKey="savings" stroke="#2196f3" strokeWidth={2} name="Savings" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="text.secondary">
                  Add transactions with dates to see monthly trends.
                </Typography>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
}

export default AnalyticsPage;
