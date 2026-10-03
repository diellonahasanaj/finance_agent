import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Avatar,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  alpha,
  useTheme,
} from "@mui/material";
import {
  Lightbulb,
  TrendingDown,
  Warning,
  CheckCircle,
  Info,
  Refresh,
  ArrowRight,
  BookmarkAdd,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import API from "../services/api";

interface Recommendation {
  id: string;
  type: string;
  title: string;
  recommendation: string;
  explanation: string;
  potential_savings?: number;
  priority: string;
  category: string;
  action_steps: string[];
}

interface RecommendationsData {
  status: string;
  recommendations: Recommendation[];
  total_count: number;
  ethical_disclaimer: string;
}

function RecommendationsPage() {
  const theme = useTheme();
  const [data, setData] = useState<RecommendationsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const response = await API.get("/recommendations/recommendations");
      setData(response.data);
      setError("");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to load recommendations"
      );
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case "Savings":
        return <CheckCircle />;
      case "Debt Reduction":
        return <TrendingDown />;
      case "Spending Optimization":
        return <Lightbulb />;
      case "Warning":
        return <Warning />;
      case "Budget Alert":
        return <Alert />;
      default:
        return <Info />;
    }
  };

  const getRecommendationColor = (priority: string) => {
    switch (priority) {
      case "high":
        return { bg: "#ff5252", icon: "#ff5252", chip: "error" };
      case "medium":
        return { bg: "#ff9800", icon: "#ff9800", chip: "warning" };
      case "low":
        return { bg: "#2196f3", icon: "#2196f3", chip: "info" };
      default:
        return { bg: "#9e9e9e", icon: "#9e9e9e", chip: "default" };
    }
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return "$0.00";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const handleSaveRecommendation = async (rec: Recommendation) => {
    try {
      await API.post("/recommendations/recommendations/save", rec);
      // You could show a toast/snackbar here
      console.log("Recommendation saved!");
    } catch (err) {
      console.error("Error saving recommendation:", err);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: '100%', overflow: 'hidden' }}>
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
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 700,
              fontSize: { xs: '1.75rem', sm: '3rem' },
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              mb: 1,
            }}
          >
            💡 AI Recommendations
          </Typography>
          <Typography variant="body1" sx={{ fontSize: { xs: '0.875rem', sm: '1rem' } }} color="text.secondary">
            Intelligent suggestions to improve your financial health
          </Typography>
        </Box>

        <IconButton
          onClick={fetchRecommendations}
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
          {/* Summary */}
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={4}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Paper
                  sx={{
                    p: 2,
                    textAlign: "center",
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(
                      theme.palette.primary.main,
                      0.1
                    )} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, fontSize: { xs: '1.5rem', sm: '2.125rem' } }}>
                    {data.total_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Recommendations
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Paper
                  sx={{
                    p: 2,
                    textAlign: "center",
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(
                      theme.palette.error.main,
                      0.1
                    )} 0%, ${alpha(theme.palette.error.main, 0.05)} 100%)`,
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.error.main, fontSize: { xs: '1.5rem', sm: '2.125rem' } }}>
                    {data.recommendations.filter((r) => r.priority === "high").length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    High Priority
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Paper
                  sx={{
                    p: 2,
                    textAlign: "center",
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(
                      theme.palette.success.main,
                      0.1
                    )} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main, fontSize: { xs: '1.5rem', sm: '2.125rem' } }}>
                    {data.recommendations.reduce((sum, r) => sum + (r.potential_savings || 0), 0).toFixed(0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Potential Monthly Savings
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>
          </Grid>

          {/* Recommendations List */}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3, mb: 4 }}>
            {data.recommendations.length > 0 ? (
              data.recommendations.map((rec, index) => {
                const colors = getRecommendationColor(rec.priority);
                const isExpanded = expandedId === rec.id;

                return (
                  <motion.div
                    key={rec.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card
                      sx={{
                        borderRadius: 3,
                        cursor: "pointer",
                        transition: "all 0.3s ease",
                        border: `2px solid ${colors.bg}22`,
                        "&:hover": {
                          transform: "translateY(-4px)",
                          boxShadow: "0 8px 30px rgba(0, 0, 0, 0.12)",
                          borderColor: colors.bg,
                        },
                      }}
                      onClick={() =>
                        setExpandedId(isExpanded ? null : rec.id)
                      }
                    >
                      <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "flex-start",
                            gap: 2,
                            mb: 2,
                            flexWrap: { xs: 'wrap', sm: 'nowrap' },
                          }}
                        >
                          <Avatar
                            sx={{
                              backgroundColor: colors.bg,
                              color: "white",
                              width: { xs: 40, sm: 48 },
                              height: { xs: 40, sm: 48 },
                            }}
                          >
                            {getRecommendationIcon(rec.type)}
                          </Avatar>

                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                                mb: 0.5,
                                flexWrap: "wrap",
                              }}
                            >
                              <Typography
                                variant="h6"
                                sx={{ fontWeight: 600, fontSize: { xs: '1rem', sm: '1.25rem' } }}
                              >
                                {rec.title}
                              </Typography>
                              <Chip
                                size="small"
                                label={rec.priority.toUpperCase()}
                                color={colors.chip as any}
                                variant="outlined"
                              />
                            </Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mb: 1, wordBreak: 'break-word' }}
                            >
                              {rec.recommendation}
                            </Typography>
                          </Box>

                          <Box sx={{ display: "flex", gap: 1, flexShrink: 0 }}>
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSaveRecommendation(rec);
                              }}
                            >
                              <BookmarkAdd fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() =>
                                setExpandedId(isExpanded ? null : rec.id)
                              }
                            >
                              <ArrowRight
                                fontSize="small"
                                sx={{
                                  transform: isExpanded
                                    ? "rotate(90deg)"
                                    : "rotate(0deg)",
                                  transition: "transform 0.3s ease",
                                }}
                              />
                            </IconButton>
                          </Box>
                        </Box>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            transition={{ duration: 0.3 }}
                          >
                            <Box
                              sx={{
                                mt: 2,
                                pt: 2,
                                borderTop: `1px solid ${alpha(
                                  theme.palette.divider,
                                  0.1
                                )}`,
                              }}
                            >
                              {/* Explanation */}
                              <Box sx={{ mb: 2 }}>
                                <Typography
                                  variant="subtitle2"
                                  sx={{ fontWeight: 600, mb: 1 }}
                                >
                                  📋 Why This Matters
                                </Typography>
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{
                                    p: 1.5,
                                    backgroundColor: alpha(
                                      colors.bg,
                                      0.05
                                    ),
                                    borderLeft: `3px solid ${colors.bg}`,
                                    borderRadius: 1,
                                    wordBreak: 'break-word',
                                  }}
                                >
                                  {rec.explanation}
                                </Typography>
                              </Box>

                              {/* Potential Savings */}
                              {rec.potential_savings && (
                                <Box sx={{ mb: 2 }}>
                                  <Typography
                                    variant="subtitle2"
                                    sx={{ fontWeight: 600, mb: 1 }}
                                  >
                                    💰 Potential Savings
                                  </Typography>
                                  <Typography
                                    variant="h6"
                                    sx={{
                                      color: theme.palette.success.main,
                                      fontWeight: 700,
                                      fontSize: { xs: '1rem', sm: '1.25rem' },
                                    }}
                                  >
                                    {formatCurrency(rec.potential_savings)}/month
                                  </Typography>
                                </Box>
                              )}

                              {/* Action Steps */}
                              <Box sx={{ mb: 2 }}>
                                <Typography
                                  variant="subtitle2"
                                  sx={{ fontWeight: 600, mb: 1 }}
                                >
                                  ✅ Action Steps
                                </Typography>
                                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                                  {rec.action_steps.map((step, idx) => (
                                    <Box
                                      key={idx}
                                      sx={{
                                        display: "flex",
                                        gap: 1,
                                        alignItems: "flex-start",
                                      }}
                                    >
                                      <Typography
                                        variant="body2"
                                        sx={{
                                          fontWeight: 600,
                                          color: colors.bg,
                                          minWidth: 20,
                                          flexShrink: 0,
                                        }}
                                      >
                                        {idx + 1}.
                                      </Typography>
                                      <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        sx={{ wordBreak: 'break-word' }}
                                      >
                                        {step}
                                      </Typography>
                                    </Box>
                                  ))}
                                </Box>
                              </Box>
                            </Box>
                          </motion.div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })
            ) : (
              <Alert severity="info">
                No recommendations at this time. Keep tracking your expenses!
              </Alert>
            )}
          </Box>

          {/* Ethical Disclaimer */}
          <Paper
            sx={{
              p: 3,
              borderRadius: 3,
              backgroundColor: alpha(theme.palette.info.main, 0.05),
              border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
            }}
          >
            <Box sx={{ display: "flex", gap: 2 }}>
              <Info color="info" sx={{ mt: 0.5 }} />
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  💡 About These Recommendations
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {data.ethical_disclaimer}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </>
      )}
    </Box>
  );
}

export default RecommendationsPage;
