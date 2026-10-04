import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  useTheme,
  alpha,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
} from "@mui/material";
import {
  ExpandMore,
  CheckCircle,
  Warning,
  Info,
  Security,
  SchoolOutlined,
  Gavel,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import API from "../services/api";

interface HowItWorksData {
  title: string;
  sections: {
    title: string;
    description: string;
  }[];
  ethical_guidelines: string[];
  disclaimer: string;
}

function TransparencyPage() {
  const theme = useTheme();
  const [data, setData] = useState<HowItWorksData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHowItWorks();
  }, []);

  const fetchHowItWorks = async () => {
    try {
      setLoading(true);
      const response = await API.get("/recommendations/how-it-works");
      setData(response.data.how_it_works);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load information");
    } finally {
      setLoading(false);
    }
  };

  const getIconForNumber = (num: number) => {
    const icons = [
      <SchoolOutlined />,
      <Info />,
      <Warning />,
      <CheckCircle />,
      <Security />,
      <Gavel />,
    ];
    return icons[Math.min(num - 1, icons.length - 1)] || <Info />;
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
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
          🔍 How It Works
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Understand how the Personal Finance Advisor Agent generates
          recommendations
        </Typography>
        <Divider />
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
          {/* Process Overview */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{ fontWeight: 600, mb: 3 }}
            >
              📋 The AI Advisory Process
            </Typography>

            <Grid container spacing={3}>
              {data.sections.map((section, index) => (
                <Grid item xs={12} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card
                      sx={{
                        borderRadius: 3,
                        borderLeft: `4px solid ${theme.palette.primary.main}`,
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box
                          sx={{
                            display: "flex",
                            gap: 2,
                            alignItems: "flex-start",
                          }}
                        >
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              width: 48,
                              height: 48,
                              borderRadius: "50%",
                              backgroundColor: alpha(
                                theme.palette.primary.main,
                                0.1
                              ),
                              color: theme.palette.primary.main,
                              flexShrink: 0,
                            }}
                          >
                            {getIconForNumber(index + 1)}
                          </Box>

                          <Box>
                            <Typography
                              variant="h6"
                              sx={{
                                fontWeight: 600,
                                mb: 1,
                              }}
                            >
                              {section.title}
                            </Typography>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ lineHeight: 1.6 }}
                            >
                              {section.description}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* Ethical Guidelines */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{ fontWeight: 600, mb: 3 }}
            >
              ✅ Our Ethical Commitment
            </Typography>

            <Grid container spacing={2}>
              {data.ethical_guidelines.map((guideline, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Paper
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        backgroundColor: alpha(
                          theme.palette.success.main,
                          0.05
                        ),
                        border: `1px solid ${alpha(
                          theme.palette.success.main,
                          0.2
                        )}`,
                        height: "100%",
                      }}
                    >
                      <Box sx={{ display: "flex", gap: 1 }}>
                        <CheckCircle
                          sx={{
                            color: theme.palette.success.main,
                            flexShrink: 0,
                            mt: 0.5,
                          }}
                        />
                        <Typography
                          variant="body2"
                          sx={{ lineHeight: 1.6 }}
                        >
                          {guideline}
                        </Typography>
                      </Box>
                    </Paper>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* FAQ Section */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{ fontWeight: 600, mb: 3 }}
            >
              ❓ Frequently Asked Questions
            </Typography>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Accordion
                defaultExpanded
                sx={{
                  borderRadius: 2,
                  "&:before": { display: "none" },
                }}
              >
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    Is this system a financial advisor?
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    No. This system is an <strong>educational tool</strong> that
                    provides suggestions based on rule-based analysis of your
                    spending patterns. It is <strong>not</strong> a substitute
                    for professional financial advice. Always consult a
                    qualified financial advisor before making major financial
                    decisions.
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ borderRadius: 2, "&:before": { display: "none" } }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    How are my recommendations generated?
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    Recommendations are generated using <strong>rule-based</strong>{" "}
                    logic. We analyze your spending patterns, budget adherence,
                    and financial metrics, then apply predefined rules (e.g.,
                    "IF food spending {'>'} 15% of income THEN suggest reducing").
                    Each recommendation includes a detailed explanation of why
                    it was generated.
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ borderRadius: 2, "&:before": { display: "none" } }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    Is my financial data private?
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    Yes. Your financial data is stored securely and is{" "}
                    <strong>never</strong> shared with third parties without
                    your explicit consent. All data remains on our secure
                    servers and is protected according to data protection
                    standards.
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ borderRadius: 2, "&:before": { display: "none" } }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    Can I trust these recommendations?
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    Recommendations are based on sound financial principles and
                    industry best practices. However, every financial situation
                    is unique. We encourage you to:
                    <br />
                    • Review recommendations in context of your life
                    <br />
                    • Consult professionals for complex decisions
                    <br />
                    • Use recommendations as a starting point for analysis
                    <br />
                    • Always make your own informed decisions
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ borderRadius: 2, "&:before": { display: "none" } }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    What categories of expenses are supported?
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="text.secondary">
                    We support the following expense categories:
                    <br />
                    • Food • Transportation • Housing • Utilities
                    <br />
                    • Entertainment • Health • Education • Shopping • Other
                    <br />
                    <br />
                    The system automatically classifies expenses based on
                    keywords and descriptions, with an option to manually
                    override the classification.
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </Box>
          </Box>

          <Divider sx={{ my: 4 }} />

          {/* Disclaimer */}
          <Alert
            severity="info"
            icon={<Gavel sx={{ fontSize: 24 }} />}
            sx={{ borderRadius: 2, mb: 4 }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
              📋 Legal Disclaimer
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {data.disclaimer}
            </Typography>
          </Alert>

          {/* Data Privacy Info */}
          <Card
            sx={{
              borderRadius: 3,
              backgroundColor: alpha(theme.palette.info.main, 0.05),
              border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                <Security
                  sx={{
                    color: theme.palette.info.main,
                    fontSize: 28,
                  }}
                />
                <Box>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 600,
                      mb: 1,
                    }}
                  >
                    🔒 Your Privacy Matters
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    We take data privacy seriously. All your financial
                    information is encrypted and stored securely. We never sell
                    your data, and recommendations are generated locally based
                    on your usage patterns.
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
}

export default TransparencyPage;
