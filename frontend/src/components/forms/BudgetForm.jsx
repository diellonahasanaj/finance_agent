
import { useState } from "react";
import API from "../../services/api";
import { Box, TextField, Button, Typography, Paper, Alert } from '@mui/material';

function BudgetForm({ onSuccess }) {
  const [form, setForm] = useState({
    category: "",
    limit: "",
    month: ""
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await API.post("/budget", { ...form, limit: parseFloat(form.limit) });
      setForm({ category: "", limit: "", month: "" });
      if (onSuccess) onSuccess();
    } catch (err) {
      setError("Failed to set budget");
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h5" sx={{ mb: 2 }}>Set Budget</Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField name="category" label="Category" value={form.category} onChange={handleChange} required />
        <TextField name="limit" type="number" label="Limit" value={form.limit} onChange={handleChange} required />
        <TextField name="month" type="month" label="Month" value={form.month} onChange={handleChange} required InputLabelProps={{ shrink: true }} />
        <Button type="submit" variant="contained" color="primary">Set</Button>
        {error && <Alert severity="error">{error}</Alert>}
      </Box>
    </Paper>
  );
}

export default BudgetForm;
