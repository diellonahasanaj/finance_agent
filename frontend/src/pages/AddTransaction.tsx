import { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  useTheme,
} from '@mui/material';
import { ArrowBack, Save } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

function AddTransaction() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [type, setType] = useState<'income' | 'expense'>('expense');
  const [formData, setFormData] = useState({
    amount: '',
    category: '',
    description: '',
    source: '',
    date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const expenseCategories = [
    'Food', 'Transportation', 'Housing', 'Utilities',
    'Entertainment', 'Health', 'Education', 'Shopping', 'Other',
  ];
  const incomeSources = ['Salary', 'Freelance', 'Investment', 'Bonus', 'Other'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = {
        amount: parseFloat(formData.amount),
        date: formData.date,
        ...(type === 'income' 
          ? { source: formData.source || 'Salary' }
          : { 
              category: formData.category || 'General',
              description: formData.description 
            }
        )
      };

      const endpoint = type === 'income' ? '/finance/income' : '/finance/expense';
      await API.post(endpoint, data);
      setSuccess(true);
      setTimeout(() => navigate('/transactions'), 1200);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string) => (e: any) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: { xs: '100%', sm: 600 }, mx: 'auto' }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/dashboard')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 4 }}>
            Add {type === 'income' ? 'Income' : 'Expense'}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>Transaction added successfully!</Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Transaction Type</InputLabel>
                  <Select
                    value={type}
                    label="Transaction Type"
                    onChange={(e) => setType(e.target.value as 'income' | 'expense')}
                  >
                    <MenuItem value="expense">Expense</MenuItem>
                    <MenuItem value="income">Income</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  inputProps={{ step: "0.01", min: 0 }}
                  required
                  value={formData.amount}
                  onChange={handleChange('amount')}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  required
                  value={formData.date}
                  onChange={handleChange('date')}
                />
              </Grid>

              {type === 'expense' ? (
                <>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Category</InputLabel>
                      <Select value={formData.category} label="Category" onChange={handleChange('category')}>
                        {expenseCategories.map((c) => (
                          <MenuItem key={c} value={c}>{c}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Description"
                      value={formData.description}
                      onChange={handleChange('description')}
                      placeholder="e.g., Grocery shopping"
                    />
                  </Grid>
                </>
              ) : (
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Source</InputLabel>
                    <Select value={formData.source} label="Source" onChange={handleChange('source')}>
                      {incomeSources.map((s) => (
                        <MenuItem key={s} value={s}>{s}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              )}

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  startIcon={<Save />}
                  sx={{ 
                    py: 1.5,
                    backgroundColor: theme.palette.primary.main,
                    '&:hover': {
                      backgroundColor: theme.palette.primary.dark,
                    }
                  }}
                >
                  {loading ? 'Saving...' : `Add ${type === 'income' ? 'Income' : 'Expense'}`}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default AddTransaction;
