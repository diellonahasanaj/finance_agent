import { useState, useEffect } from "react";
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Grid,
  Card,
  CardContent,
  useTheme,
  CircularProgress,
  Alert,
  MenuItem,
  FormControl,
  InputLabel,
  Select
} from '@mui/material';
import { ArrowBack, Save, TrendingUp } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
// @ts-ignore
import API from '../services/api';

interface Budget {
  _id: string;
  category: string;
  limit: number;
  month: string;
  created_at: string;
}

function SetBudget() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    category: '',
    limit: '',
    month: new Date().toISOString().slice(0, 7) // YYYY-MM format
  });
  const [existingBudgets, setExistingBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      const response = await API.get('/finance/budget');
      setExistingBudgets(response.data);
    } catch (err: any) {
      console.error('Failed to fetch budgets:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const data = {
        category: formData.category,
        limit: parseFloat(formData.limit),
        month: formData.month
      };

      await API.post('/finance/budget', data);
      setSuccess(true);
      
      // Clear form
      setFormData({
        category: '',
        limit: '',
        month: new Date().toISOString().slice(0, 7)
      });

      // Refresh budgets list
      await fetchBudgets();

      // Navigate back after a short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to set budget');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string) => (e: any) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const categories = [
    'Food & Dining',
    'Transportation',
    'Shopping',
    'Entertainment',
    'Bills & Utilities',
    'Healthcare',
    'Education',
    'Personal Care',
    'Travel',
    'Debt Payments',
    'Savings & Investments',
    'Other'
  ];

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 800, mx: 'auto' }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/dashboard')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Set New Budget Form */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h4" sx={{ fontWeight: 600, mb: 4 }}>
                Set Budget
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  Budget set successfully! Redirecting to dashboard...
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Category</InputLabel>
                      <Select
                        value={formData.category}
                        label="Category"
                        onChange={handleChange('category')}
                      >
                        {categories.map((category) => (
                          <MenuItem key={category} value={category}>
                            {category}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Budget Limit"
                      type="number"
                      inputProps={{ step: "0.01", min: 0 }}
                      required
                      value={formData.limit}
                      onChange={handleChange('limit')}
                      placeholder="0.00"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Month"
                      type="month"
                      required
                      value={formData.month}
                      onChange={handleChange('month')}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                      sx={{ 
                        py: 1.5,
                        backgroundColor: theme.palette.primary.main,
                        '&:hover': {
                          backgroundColor: theme.palette.primary.dark,
                        }
                      }}
                    >
                      {loading ? 'Setting Budget...' : 'Set Budget'}
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Existing Budgets */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <TrendingUp sx={{ mr: 1, color: theme.palette.primary.main }} />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Current Budgets
                </Typography>
              </Box>

              {existingBudgets.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No budgets set yet. Create your first budget!
                </Typography>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {existingBudgets.map((budget) => (
                    <Box
                      key={budget._id}
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        backgroundColor: theme.palette.background.default,
                        border: `1px solid ${theme.palette.divider}`
                      }}
                    >
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {budget.category}
                      </Typography>
                      <Typography variant="h6" color="primary.main">
                        ${budget.limit.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {budget.month}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default SetBudget;
