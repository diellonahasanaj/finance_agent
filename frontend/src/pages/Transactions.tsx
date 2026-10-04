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
  Pagination,
  Tooltip,
  useTheme,
  alpha,
} from "@mui/material";
import { Edit, Delete, Search, Add, Refresh } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

interface Transaction {
  _id: string;
  type: "income" | "expense";
  amount: number;
  date: string;
  category?: string;
  source?: string;
  description?: string;
  label?: string;
}

interface TransactionsResponse {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const EXPENSE_CATEGORIES = [
  "Food", "Transportation", "Housing", "Utilities",
  "Entertainment", "Health", "Education", "Shopping", "Other",
];

const INCOME_SOURCES = ["Salary", "Freelance", "Investment", "Bonus", "Other"];

function Transactions() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [data, setData] = useState<TransactionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [month, setMonth] = useState("");
  const [page, setPage] = useState(1);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selected, setSelected] = useState<Transaction | null>(null);
  const [editForm, setEditForm] = useState({
    amount: "",
    date: "",
    category: "",
    source: "",
    description: "",
  });
  const [saving, setSaving] = useState(false);

  const currency = localStorage.getItem("currency") || "USD";
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const params: Record<string, string | number> = { page, page_size: 10 };
      if (search) params.search = search;
      if (typeFilter) params.type = typeFilter;
      if (month) params.month = month;
      const response = await API.get("/finance/transactions", { params });
      setData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load transactions");
    } finally {
      setLoading(false);
    }
  }, [page, search, typeFilter, month]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const openEdit = (tx: Transaction) => {
    setSelected(tx);
    setEditForm({
      amount: String(tx.amount),
      date: tx.date?.slice(0, 10) || "",
      category: tx.category || "Other",
      source: tx.source || "Salary",
      description: tx.description || "",
    });
    setEditOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      const payload = {
        amount: parseFloat(editForm.amount),
        date: editForm.date,
        ...(selected.type === "expense"
          ? { category: editForm.category, description: editForm.description }
          : { source: editForm.source }),
      };
      const endpoint =
        selected.type === "income"
          ? `/finance/income/${selected._id}`
          : `/finance/expense/${selected._id}`;
      await API.put(endpoint, payload);
      setSuccess("Transaction updated successfully");
      setEditOpen(false);
      fetchTransactions();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update transaction");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      const endpoint =
        selected.type === "income"
          ? `/finance/income/${selected._id}`
          : `/finance/expense/${selected._id}`;
      await API.delete(endpoint);
      setSuccess("Transaction deleted successfully");
      setDeleteOpen(false);
      fetchTransactions();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete transaction");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3, flexWrap: "wrap", gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Transactions</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your income and expense records
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchTransactions}><Refresh /></IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<Add />} onClick={() => navigate("/add-transaction")}>
            Add Transaction
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess("")}>{success}</Alert>}

      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
            <TextField
              size="small"
              placeholder="Search transactions..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              InputProps={{ startAdornment: <Search sx={{ mr: 1, color: "text.secondary" }} /> }}
              sx={{ minWidth: 220 }}
            />
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Type</InputLabel>
              <Select value={typeFilter} label="Type" onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="income">Income</MenuItem>
                <MenuItem value="expense">Expense</MenuItem>
              </Select>
            </FormControl>
            <TextField
              size="small"
              type="month"
              label="Month"
              value={month}
              onChange={(e) => { setMonth(e.target.value); setPage(1); }}
              InputLabelProps={{ shrink: true }}
            />
            {(search || typeFilter || month) && (
              <Button size="small" onClick={() => { setSearch(""); setTypeFilter(""); setMonth(""); setPage(1); }}>
                Clear filters
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
              <CircularProgress />
            </Box>
          ) : !data?.items.length ? (
            <Box sx={{ textAlign: "center", py: 8, px: 3 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No transactions found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {search || typeFilter || month
                  ? "Try adjusting your filters."
                  : "Start by adding your first income or expense."}
              </Typography>
              <Button variant="contained" startIcon={<Add />} onClick={() => navigate("/add-transaction")}>
                Add Transaction
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: alpha(theme.palette.primary.main, 0.05) }}>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Category / Source</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.items.map((tx) => (
                      <TableRow key={tx._id} hover>
                        <TableCell>{tx.date?.slice(0, 10)}</TableCell>
                        <TableCell>
                          <Chip
                            label={tx.type}
                            size="small"
                            color={tx.type === "income" ? "success" : "error"}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>{tx.description || tx.label || "—"}</TableCell>
                        <TableCell>{tx.category || tx.source || "—"}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600, color: tx.type === "income" ? "success.main" : "error.main" }}>
                          {tx.type === "income" ? "+" : "-"}{formatCurrency(tx.amount)}
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => openEdit(tx)}><Edit fontSize="small" /></IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => { setSelected(tx); setDeleteOpen(true); }}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              {data.total_pages > 1 && (
                <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
                  <Pagination count={data.total_pages} page={page} onChange={(_, p) => setPage(p)} color="primary" />
                </Box>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Transaction</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <TextField label="Amount" type="number" value={editForm.amount} onChange={(e) => setEditForm({ ...editForm, amount: e.target.value })} fullWidth />
            <TextField label="Date" type="date" value={editForm.date} onChange={(e) => setEditForm({ ...editForm, date: e.target.value })} fullWidth InputLabelProps={{ shrink: true }} />
            {selected?.type === "expense" ? (
              <>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select value={editForm.category} label="Category" onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}>
                    {EXPENSE_CATEGORIES.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                  </Select>
                </FormControl>
                <TextField label="Description" value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} fullWidth />
              </>
            ) : (
              <FormControl fullWidth>
                <InputLabel>Source</InputLabel>
                <Select value={editForm.source} label="Source" onChange={(e) => setEditForm({ ...editForm, source: e.target.value })}>
                  {INCOME_SOURCES.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                </Select>
              </FormControl>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveEdit} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)}>
        <DialogTitle>Delete Transaction</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete this {selected?.type}? This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete} disabled={saving}>
            {saving ? "Deleting..." : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Transactions;
