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
  BarChart,
  Bar,
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
import { motion } from "framer-motion";
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
  "#ff7300",
  "#00d084",
  "#2196f3",
  "#ff6b6b",
  "#ffd666",
  "#95de64",
  "#5cdbd3",
  "#9254de",
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
      // Fetch financial dashboard data
      const response = await API.get("/finance/dashboard");
      
      // Transform data for analytics
      const transformedData: AnalyticsData = {
        categoryBreakdown: Object.entries(
          response.data.categoryBreakdown || {}
        ).map(([category, amount]: [string, any]) => ({
          category,
          amount: Number(amount),
        })),
        monthlyTrends: [
          {
            month: "Week 1",
            income: response.data.total_income * 0.25,
            expenses: response.data.total_expenses * 0.3,
            savings: response.data.total_income * 0.25 - response.data.total_expenses * 0.3,
          },
          {
            month: "Week 2",
            income: response.data.total_income * 0.25,
            expenses: response.data.total_expenses * 0.25,
            savings: response.data.total_income * 0.25 - response.data.total_expenses * 0.25,
          },
          {
            month: "Week 3",
            income: response.data.total_income * 0.25,
            expenses: response.data.total_expenses * 0.28,
            savings: response.data.total_income * 0.25 - response.data.total_expenses * 0.28,
          },
          {
            month: "Week 4",
            income: response.data.total_income * 0.25,
            expenses: response.data.total_expenses * 0.17,
            savings: response.data.total_income * 0.25 - response.data.total_expenses * 0.17,
          },
        ],
        budgetStatus: {
          total_budget: response.data.budgets?.reduce(
            (sum: number, b: any) => sum + b.limit,
            0
          ) || 0,
          total_spent: response.data.total_expenses || 0,
          percentage:
            ((response.data.total_expenses || 0) /
              (response.data.budgets?.reduce((sum: number, b: any) => sum + b.limit, 0) || 1)) *
            100,
        },
        savingsRate:
          response.data.total_income > 0
            ? ((response.data.total_income - response.data.total_expenses) /
                response.data.total_income) *
              100
            : 0,
      };

      setData(transformedData);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
          flexWrap: "wrap",
          gap: 2,
        }}
      >
        <Box>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              mb: 1,
            }}
          >
            📊 Financial Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Detailed insights into your spending patterns and trends
          </Typography>
        </Box>

        <Tooltip title="Refresh Analytics">
          <IconButton
            onClick={fetchAnalyticsData}
            disabled={loading}
            sx={{
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
              "&:hover": {
                backgroundColor: alpha(theme.palette.primary.main, 0.2),
              },
            }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "60vh",
          }}
        >
          <CircularProgress size={60} />
        </Box>
      )}

      {/* Error State */}
      {error && !loading && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Content */}
      {!loading && data && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Paper
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(
                      theme.palette.success.main,
                      0.1
                    )} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <TrendingUp
                      sx={{
                        color: theme.palette.success.main,
                        fontSize: 24,
                      }}
                    />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Savings Rate
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          color: theme.palette.success.main,
                        }}
                      >
                        {data.savingsRate.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Paper
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(
                      theme.palette.warning.main,
                      0.1
                    )} 0%, ${alpha(theme.palette.warning.main, 0.05)} 100%)`,
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <TrendingDown
                      sx={{
                        color: theme.palette.warning.main,
                        fontSize: 24,
                      }}
                    />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Budget Usage
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          color: theme.palette.warning.main,
                        }}
                      >
                        {data.budgetStatus.percentage.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </motion.div>
            </Grid>
          </Grid>

          {/* Charts Grid */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Spending by Category */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card sx={{ height: "100%", borderRadius: 3 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, mb: 3 }}
                    >
                      💰 Spending by Category
                    </Typography>
                    {data.categoryBreakdown.length > 0 ? (
                      <ResponsiveContainer
                        width="100%"
                        height={300}
                      >
                        <PieChart>
                          <Pie
                            data={data.categoryBreakdown}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ category, percent }) =>
                              `${category}: ${(percent * 100).toFixed(0)}%`
                            }
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="amount"
                          >
                            {data.categoryBreakdown.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <ChartTooltip
                            formatter={(value) => formatCurrency(Number(value))}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <Typography color="text.secondary">
                        No spending data available
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Category Breakdown Table */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card sx={{ height: "100%", borderRadius: 3 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography
                      variant="h6"
                      sx={{ fontWeight: 600, mb: 3 }}
                    >
                      📋 Category Breakdown
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 2,
                      }}
                    >
                      {data.categoryBreakdown.length > 0 ? (
                        data.categoryBreakdown.map((category, index) => {
                          const total = data.categoryBreakdown.reduce(
                            (sum, c) => sum + c.amount,
                            0
                          );
                          const percentage = (
                            (category.amount / total) *
                            100
                          ).toFixed(1);

                          return (
                            <Box key={category.category}>
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  mb: 0.5,
                                }}
                              >
                                <Typography variant="body2">
                                  {category.category}
                                </Typography>
                                <Typography
                                  variant="body2"
                                  sx={{ fontWeight: 600 }}
                                >
                                  {formatCurrency(category.amount)} ({percentage}%)
                                </Typography>
                              </Box>
                              <Box
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: alpha(
                                    theme.palette.divider,
                                    0.2
                                  ),
                                  overflow: "hidden",
                                }}
                              >
                                <Box
                                  sx={{
                                    height: "100%",
                                    width: `${percentage}%`,
                                    backgroundColor:
                                      COLORS[index % COLORS.length],
                                    borderRadius: 3,
                                    transition: "width 0.3s ease",
                                  }}
                                />
                              </Box>
                            </Box>
                          );
                        })
                      ) : (
                        <Typography color="text.secondary">
                          No category data available
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>

          {/* Monthly Trends */}
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card sx={{ borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                    📈 Monthly Trends
                  </Typography>
                  {data.monthlyTrends.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={data.monthlyTrends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <ChartTooltip
                          formatter={(value) => formatCurrency(Number(value))}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="income"
                          stroke="#00d084"
                          strokeWidth={2}
                          name="Income"
                        />
                        <Line
                          type="monotone"
                          dataKey="expenses"
                          stroke="#ff7300"
                          strokeWidth={2}
                          name="Expenses"
                        />
                        <Line
                          type="monotone"
                          dataKey="savings"
                          stroke="#2196f3"
                          strokeWidth={2}
                          name="Savings"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <Typography color="text.secondary">
                      No trend data available
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Additional Insights */}
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <Card sx={{ borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    💡 Key Insights
                  </Typography>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      ✅ Your savings rate is{" "}
                      <strong>{data.savingsRate.toFixed(1)}%</strong> of your
                      income. Target: 20%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      📊 You've allocated{" "}
                      <strong>${data.budgetStatus.total_budget.toFixed(2)}</strong> in
                      budgets and spent{" "}
                      <strong>${data.budgetStatus.total_spent.toFixed(2)}</strong>
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      🎯 Most spending is in{" "}
                      <strong>
                        {data.categoryBreakdown.length > 0
                          ? data.categoryBreakdown[0].category
                          : "N/A"}
                      </strong>
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

export default AnalyticsPage;
