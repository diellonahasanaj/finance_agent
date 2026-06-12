import { useState, useEffect, useCallback } from "react";
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
  Select,
  Chip,
} from "@mui/material";
import { ArrowBack, Save, AutoAwesome } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

const DEFAULT_CATEGORIES = [
  "Food",
  "Transportation",
  "Housing",
  "Utilities",
  "Entertainment",
  "Health",
  "Education",
  "Shopping",
  "Other",
];

function AddExpense() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    amount: "",
    category: "",
    description: "",
    date: new Date().toISOString().split("T")[0],
  });
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [classification, setClassification] = useState<{
    category: string;
    confidence: number;
    explanation: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    API.get("/recommendations/categories")
      .then((res) => {
        if (res.data?.categories?.length) {
          setCategories(res.data.categories);
        }
      })
      .catch(() => {});
  }, []);

  const classifyExpense = useCallback(async (description: string) => {
    if (!description || description.length < 3) {
      setClassification(null);
      return;
    }
    try {
      setClassifying(true);
      const response = await API.post("/recommendations/classify-expense", {
        title: description,
        description,
      });
      const result = response.data;
      setClassification({
        category: result.classified_category,
        confidence: result.confidence,
        explanation: result.explanation,
      });
      if (!formData.category) {
        setFormData((prev) => ({ ...prev, category: result.classified_category }));
      }
    } catch {
      setClassification(null);
    } finally {
      setClassifying(false);
    }
  }, [formData.category]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (formData.description) {
        classifyExpense(formData.description);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [formData.description, classifyExpense]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);

    try {
      await API.post("/finance/expense", {
        amount: parseFloat(formData.amount),
        category: formData.category || classification?.category || "Other",
        description: formData.description,
        date: formData.date,
      });
      setSuccess(true);
      setFormData({
        amount: "",
        category: "",
        description: "",
        date: new Date().toISOString().split("T")[0],
      });
      setClassification(null);
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add expense");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string) => (e: any) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 600, mx: "auto" }}>
      <Button startIcon={<ArrowBack />} onClick={() => navigate("/dashboard")} sx={{ mb: 2 }}>
        Back to Dashboard
      </Button>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Add Expense
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Expenses are automatically categorized using rule-based keyword matching.
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 3 }}>Expense added successfully!</Alert>}

          {classification && (
            <Alert
              severity="info"
              icon={<AutoAwesome />}
              sx={{ mb: 3 }}
            >
              Suggested category: <strong>{classification.category}</strong>{" "}
              ({(classification.confidence * 100).toFixed(0)}% confidence). {classification.explanation}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  inputProps={{ step: "0.01", min: 0 }}
                  required
                  value={formData.amount}
                  onChange={handleChange("amount")}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  required
                  value={formData.date}
                  onChange={handleChange("date")}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  required
                  value={formData.description}
                  onChange={handleChange("description")}
                  placeholder="e.g. Grocery shopping at supermarket"
                  helperText={classifying ? "Classifying..." : "Type a description to auto-suggest a category"}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category}
                    label="Category"
                    onChange={handleChange("category")}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category}
                        {classification?.category === category && (
                          <Chip label="Suggested" size="small" sx={{ ml: 1 }} />
                        )}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
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
                    backgroundColor: theme.palette.error.main,
                    "&:hover": { backgroundColor: theme.palette.error.dark },
                  }}
                >
                  {loading ? "Adding Expense..." : "Add Expense"}
                </Button>
              </Grid>
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default AddExpense;
