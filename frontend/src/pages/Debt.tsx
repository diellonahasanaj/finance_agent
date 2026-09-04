import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Tooltip,
  useTheme,
  alpha,
} from "@mui/material";
import { Edit, Delete, Add, Refresh, ArrowBack, CheckCircle } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

interface Debt {
  _id: string;
  amount: number;
  interest_rate: number;
  monthly_payment: number;
  due_date: string;
  creditor: string;
  description?: string;
  is_paid_off: boolean;
  created_at: string;
  updated_at?: string;
}

function Debt() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [data, setData] = useState<Debt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [addOpen, setAddOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selected, setSelected] = useState<Debt | null>(null);
  const [form, setForm] = useState({
    amount: "",
    interest_rate: "",
    monthly_payment: "",
    due_date: "",
    creditor: "",
    description: "",
    is_paid_off: false,
  });
  const [saving, setSaving] = useState(false);

  const currency = localStorage.getItem("currency") || "USD";
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);

  const fetchDebts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await API.get("/finance/debt");
      setData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load debt records");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDebts();
  }, [fetchDebts]);

  const handleAdd = () => {
    setForm({
      amount: "",
      interest_rate: "",
      monthly_payment: "",
      due_date: "",
      creditor: "",
      description: "",
      is_paid_off: false,
    });
    setAddOpen(true);
  };

  const handleEdit = (debt: Debt) => {
    setSelected(debt);
    setForm({
      amount: debt.amount.toString(),
      interest_rate: debt.interest_rate.toString(),
      monthly_payment: debt.monthly_payment.toString(),
      due_date: debt.due_date,
      creditor: debt.creditor,
      description: debt.description || "",
      is_paid_off: debt.is_paid_off,
    });
    setEditOpen(true);
  };

  const handleDelete = (debt: Debt) => {
    setSelected(debt);
    setDeleteOpen(true);
  };

  const handleSaveAdd = async () => {
    try {
      setSaving(true);
      await API.post("/finance/debt", {
        amount: parseFloat(form.amount),
        interest_rate: parseFloat(form.interest_rate),
        monthly_payment: parseFloat(form.monthly_payment),
        due_date: form.due_date,
        creditor: form.creditor,
        description: form.description,
        is_paid_off: form.is_paid_off,
      });
      setSuccess("Debt added successfully");
      setAddOpen(false);
      fetchDebts();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to add debt");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!selected) return;
    try {
      setSaving(true);
      await API.put(`/finance/debt/${selected._id}`, {
        amount: parseFloat(form.amount),
        interest_rate: parseFloat(form.interest_rate),
        monthly_payment: parseFloat(form.monthly_payment),
        due_date: form.due_date,
        creditor: form.creditor,
        description: form.description,
        is_paid_off: form.is_paid_off,
      });
      setSuccess("Debt updated successfully");
      setEditOpen(false);
      fetchDebts();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update debt");
    } finally {
      setSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selected) return;
    try {
      setSaving(true);
      await API.delete(`/finance/debt/${selected._id}`);
      setSuccess("Debt deleted successfully");
      setDeleteOpen(false);
      fetchDebts();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete debt");
    } finally {
      setSaving(false);
    }
  };

  const handleTogglePaidOff = async (debt: Debt) => {
    try {
      setSaving(true);
      await API.put(`/finance/debt/${debt._id}`, {
        ...debt,
        is_paid_off: !debt.is_paid_off,
      });
      setSuccess(`Debt marked as ${debt.is_paid_off ? "unpaid" : "paid off"}`);
      fetchDebts();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update debt status");
    } finally {
      setSaving(false);
    }
  };

  if (loading && data.length === 0) {
    return (
      <Box sx={{ p: 3, display: "flex", justifyContent: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  const activeDebts = data.filter(d => !d.is_paid_off);
  const paidOffDebts = data.filter(d => d.is_paid_off);
  const totalDebt = activeDebts.reduce((sum, d) => sum + d.amount, 0);
  const totalMonthlyPayment = activeDebts.reduce((sum, d) => sum + d.monthly_payment, 0);

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
        <Box>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/dashboard")}
            sx={{ mb: 2 }}
          >
            Back to Dashboard
          </Button>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            Debt Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Track and manage your debts
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={handleAdd}
            sx={{
              backgroundColor: theme.palette.error.main,
              "&:hover": { backgroundColor: theme.palette.error.dark },
            }}
          >
            Add Debt
          </Button>
          <IconButton onClick={fetchDebts} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess("")}>
          {success}
        </Alert>
      )}

      {/* Summary Cards */}
      <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
        <Card sx={{ flex: 1, minWidth: 200, borderRadius: 2 }}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Total Debt
            </Typography>
            <Typography variant="h4" color="error.main" sx={{ fontWeight: 600 }}>
              {formatCurrency(totalDebt)}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200, borderRadius: 2 }}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Monthly Payments
            </Typography>
            <Typography variant="h4" color="warning.main" sx={{ fontWeight: 600 }}>
              {formatCurrency(totalMonthlyPayment)}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200, borderRadius: 2 }}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Active Debts
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {activeDebts.length}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200, borderRadius: 2 }}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Paid Off
            </Typography>
            <Typography variant="h4" color="success.main" sx={{ fontWeight: 600 }}>
              {paidOffDebts.length}
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Active Debts Table */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Active Debts
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Creditor</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Interest Rate</TableCell>
                  <TableCell>Monthly Payment</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activeDebts.map((debt) => (
                  <TableRow key={debt._id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {debt.creditor}
                      </Typography>
                      {debt.description && (
                        <Typography variant="caption" color="text.secondary">
                          {debt.description}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell sx={{ fontWeight: 600, color: theme.palette.error.main }}>
                      {formatCurrency(debt.amount)}
                    </TableCell>
                    <TableCell>{debt.interest_rate}%</TableCell>
                    <TableCell>{formatCurrency(debt.monthly_payment)}</TableCell>
                    <TableCell>{debt.due_date}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Mark as Paid">
                        <IconButton size="small" onClick={() => handleTogglePaidOff(debt)} color="success">
                          <CheckCircle fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleEdit(debt)}>
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDelete(debt)} color="error">
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {activeDebts.length === 0 && (
            <Box sx={{ textAlign: "center", py: 4 }}>
              <Typography variant="body2" color="text.secondary">
                No active debts. Great job!
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Paid Off Debts */}
      {paidOffDebts.length > 0 && (
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Paid Off Debts
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Creditor</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Interest Rate</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paidOffDebts.map((debt) => (
                    <TableRow key={debt._id} hover sx={{ opacity: 0.6 }}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {debt.creditor}
                        </Typography>
                      </TableCell>
                      <TableCell sx={{ textDecoration: "line-through" }}>
                        {formatCurrency(debt.amount)}
                      </TableCell>
                      <TableCell>{debt.interest_rate}%</TableCell>
                      <TableCell align="center">
                        <Tooltip title="Mark as Unpaid">
                          <IconButton size="small" onClick={() => handleTogglePaidOff(debt)}>
                            <CheckCircle fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton size="small" onClick={() => handleDelete(debt)} color="error">
                            <Delete fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Add Dialog */}
      <Dialog open={addOpen} onClose={() => setAddOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Debt</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
            <TextField
              label="Creditor"
              fullWidth
              value={form.creditor}
              onChange={(e) => setForm({ ...form, creditor: e.target.value })}
              placeholder="e.g., Bank of America"
            />
            <TextField
              label="Amount"
              type="number"
              fullWidth
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              inputProps={{ step: "0.01", min: 0 }}
            />
            <TextField
              label="Interest Rate (%)"
              type="number"
              fullWidth
              value={form.interest_rate}
              onChange={(e) => setForm({ ...form, interest_rate: e.target.value })}
              inputProps={{ step: "0.1", min: 0 }}
            />
            <TextField
              label="Monthly Payment"
              type="number"
              fullWidth
              value={form.monthly_payment}
              onChange={(e) => setForm({ ...form, monthly_payment: e.target.value })}
              inputProps={{ step: "0.01", min: 0 }}
            />
            <TextField
              label="Due Date"
              type="date"
              fullWidth
              value={form.due_date}
              onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="e.g., Credit card, Mortgage, etc."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveAdd} variant="contained" disabled={saving}>
            {saving ? "Adding..." : "Add Debt"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Debt</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
            <TextField
              label="Creditor"
              fullWidth
              value={form.creditor}
              onChange={(e) => setForm({ ...form, creditor: e.target.value })}
            />
            <TextField
              label="Amount"
              type="number"
              fullWidth
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              inputProps={{ step: "0.01", min: 0 }}
            />
            <TextField
              label="Interest Rate (%)"
              type="number"
              fullWidth
              value={form.interest_rate}
              onChange={(e) => setForm({ ...form, interest_rate: e.target.value })}
              inputProps={{ step: "0.1", min: 0 }}
            />
            <TextField
              label="Monthly Payment"
              type="number"
              fullWidth
              value={form.monthly_payment}
              onChange={(e) => setForm({ ...form, monthly_payment: e.target.value })}
              inputProps={{ step: "0.01", min: 0 }}
            />
            <TextField
              label="Due Date"
              type="date"
              fullWidth
              value={form.due_date}
              onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained" disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Delete Debt</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this debt record from{" "}
            <strong>{selected?.creditor}</strong>?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} variant="contained" color="error" disabled={saving}>
            {saving ? "Deleting..." : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Debt;
