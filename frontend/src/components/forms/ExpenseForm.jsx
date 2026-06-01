
import API from "../../services/api";
import { Box, TextField, Button, Typography, Paper, Alert } from '@mui/material';
import { useState } from "react";

function ExpenseForm({ onSuccess }) {
	const [form, setForm] = useState({
		amount: "",
		category: "",
		description: "",
		date: ""
	});
	const [error, setError] = useState("");

	const handleChange = (e) => {
		setForm({ ...form, [e.target.name]: e.target.value });
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError("");
		try {
			await API.post("/expense", form);
			setForm({ amount: "", category: "", description: "", date: "" });
			if (onSuccess) onSuccess();
		} catch (err) {
			setError("Failed to add expense");
		}
	};

	return (
		<Paper sx={{ p: 3, maxWidth: 400, mx: 'auto' }}>
			<Typography variant="h5" sx={{ mb: 2 }}>Add Expense</Typography>
			<Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
				<TextField name="amount" type="number" label="Amount" value={form.amount} onChange={handleChange} required />
				<TextField name="category" label="Category" value={form.category} onChange={handleChange} required />
				<TextField name="description" label="Description" value={form.description} onChange={handleChange} />
				<TextField name="date" type="date" label="Date" value={form.date} onChange={handleChange} required InputLabelProps={{ shrink: true }} />
				<Button type="submit" variant="contained" color="primary">Add</Button>
				{error && <Alert severity="error">{error}</Alert>}
			</Box>
		</Paper>
	);
}

export default ExpenseForm;
