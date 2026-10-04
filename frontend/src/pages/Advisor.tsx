import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  Stack,
  Alert,
  Divider,
  useTheme,
} from '@mui/material';
import {
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  AttachMoney as AttachMoneyIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import AdvisorChat from '../components/dashboard/AdvisorChat';

const Advisor: React.FC = () => {
  const theme = useTheme();

  const tips = [
    {
      title: 'Smart Budgeting',
      description: 'Ask me to analyze your spending patterns and create personalized budgets.',
      icon: AttachMoneyIcon,
    },
    {
      title: 'Expense Optimization',
      description: 'Learn how to reduce expenses in specific categories without sacrificing quality.',
      icon: TrendingUpIcon,
    },
    {
      title: 'Financial Insights',
      description: 'Get real-time insights into your financial health and receive actionable recommendations.',
      icon: LightbulbIcon,
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          Financial Advisor
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Get personalized financial guidance powered by AI. Ask questions about your spending, budgets, and financial goals.
        </Typography>
      </Box>

      {/* Disclaimer */}
      <Alert severity="info" sx={{ mb: 3 }} icon={<InfoIcon />}>
        <Typography variant="body2">
          <strong>Important Disclaimer:</strong> This system provides educational financial guidance and does not replace professional financial advice. 
          All recommendations are based on rule-based analysis of your financial data. 
          Consult a qualified financial advisor before making major financial decisions.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {/* Chat Section */}
        <Grid item xs={12} md={8}>
          <AdvisorChat />
        </Grid>

        {/* Tips Section */}
        <Grid item xs={12} md={4}>
          <Stack spacing={2}>
            <Paper elevation={0} sx={{ p: 2, backgroundColor: 'background.default' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Tips for Better Questions
              </Typography>
              <Stack spacing={1.5} divider={<Divider />}>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Be Specific
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    "How much do I spend on food?" works better than "Tell me about spending"
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Ask for Advice
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Ask for recommendations: "Should I reduce food spending?" or "How can I save more?"
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Compare Patterns
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Ask comparisons: "What's my income vs expenses?" or "Compare my top categories"
                  </Typography>
                </Box>
              </Stack>
            </Paper>

            {/* Feature Cards */}
            <Stack spacing={1.5}>
              {tips.map((tip, idx) => {
                const Icon = tip.icon;
                return (
                  <Card key={idx} elevation={1}>
                    <CardContent sx={{ pb: 2, '&:last-child': { pb: 2 } }}>
                      <Stack direction="row" spacing={1.5}>
                        <Icon
                          sx={{
                            color: theme.palette.primary.main,
                            fontSize: 28,
                            flexShrink: 0,
                            mt: 0.5,
                          }}
                        />
                        <Box flex={1}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {tip.title}
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                            {tip.description}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                );
              })}
            </Stack>

            {/* Example Questions */}
            <Paper elevation={0} sx={{ p: 2, backgroundColor: 'background.default' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1.5 }}>
                Example Questions
              </Typography>
              <Stack spacing={1}>
                {[
                  'How much is my income vs expenses?',
                  'What are my spending categories?',
                  'Which category has the highest spending?',
                  'Should I reduce food spending?',
                  'How can I save more money?',
                  'What\'s my current financial health?',
                ].map((q, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{
                      p: 1,
                      backgroundColor: theme.palette.mode === 'dark' ? '#333' : '#f5f5f5',
                      borderRadius: 1,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.light,
                        color: 'white',
                      },
                    }}
                  >
                    • {q}
                  </Typography>
                ))}
              </Stack>
            </Paper>
          </Stack>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Advisor;
