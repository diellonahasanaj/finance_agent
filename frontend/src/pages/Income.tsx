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
  useMediaQuery,
} from "@mui/material";
import { Edit, Delete, Search, Add, Refresh, ArrowBack } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

interface Income {
  _id: string;
  amount: number;
  date: string;
  source: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

interface IncomeResponse {
  items: Income[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const INCOME_SOURCES = ["Salary", "Freelance", "Investment", "Bonus", "Other"];

function Income() {
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [data, setData] = useState<IncomeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");
  const [month, setMonth] = useState("");
  const [page, setPage] = useState(1);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selected, setSelected] = useState<Income | null>(null);
  const [editForm, setEditForm] = useState({
    amount: "",
    date: "",
    source: "",
    description: "",
  });
  const [saving, setSaving] = useState(false);

  const currency = localStorage.getItem("currency") || "USD";
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);

  const fetchIncome = useCallback(async () => {
    try {
      setLoading(true);
      const params: Record<string, string | number> = { page, page_size: 10 };
      if (search) params.search = search;
      if (month) params.month = month;
      const response = await API.get("/finance/income", { params });
      setData(response.data);
      setError("");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load income records");
    } finally {
      setLoading(false);
    }
  }, [page, search, month]);

  useEffect(() => {
    fetchIncome();
  }, [fetchIncome]);

  const handleEdit = (income: Income) => {
    setSelected(income);
    setEditForm({
      amount: income.amount.toString(),
      date: income.date,
      source: income.source,
      description: income.description || "",
    });
    setEditOpen(true);
  };

  const handleDelete = (income: Income) => {
    setSelected(income);
    setDeleteOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!selected) return;
    try {
      setSaving(true);
      await API.put(`/finance/income/${selected._id}`, {
        amount: parseFloat(editForm.amount),
        date: editForm.date,
        source: editForm.source,
        description: editForm.description,
      });
      setSuccess("Income updated successfully");
      setEditOpen(false);
      fetchIncome();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update income");
    } finally {
      setSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selected) return;
    try {
      setSaving(true);
      await API.delete(`/finance/income/${selected._id}`);
      setSuccess("Income deleted successfully");
      setDeleteOpen(false);
      fetchIncome();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete income");
    } finally {
      setSaving(false);
    }
  };

  const handleClearFilters = () => {
    setSearch("");
    setMonth("");
    setPage(1);
  };

  if (loading && !data) {
    return (
      <Box sx={{ p: 3, display: "flex", justifyContent: "center" }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/dashboard")}
            sx={{ mb: { xs: 1, sm: 2 } }}
          >
            Back
          </Button>
          <Typography variant={{ xs: "h5", sm: "h4" }} sx={{ fontWeight: 600 }}>
            Income Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage your income sources and records
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={() => navigate("/add-transaction")}
            sx={{
              backgroundColor: theme.palette.success.main,
              "&:hover": { backgroundColor: theme.palette.success.dark },
              display: { xs: 'none', sm: 'flex' }
            }}
          >
            Add Income
          </Button>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={() => navigate("/add-transaction")}
            sx={{
              backgroundColor: theme.palette.success.main,
              "&:hover": { backgroundColor: theme.palette.success.dark },
              display: { xs: 'flex', sm: 'none' },
              minWidth: 'auto'
            }}
          >
            <Add />
          </Button>
          <IconButton onClick={fetchIncome} disabled={loading}>
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

      {/* Filters */}
      <Card sx={{ mb: 3, borderRadius: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
            <TextField
              label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: "text.secondary" }} />,
              }}
              sx={{ minWidth: { xs: 150, sm: 250 }, flex: { xs: 1, sm: 'auto' } }}
            />
            <TextField
              label="Month"
              type="month"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: { xs: 130, sm: 180 }, flex: { xs: 1, sm: 'auto' } }}
            />
            {(search || month) && (
              <Button onClick={handleClearFilters} variant="outlined" size="small">
                Clear
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {data && (
        <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
          <Card sx={{ flex: 1, minWidth: { xs: 140, sm: 200 }, borderRadius: 2 }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Records
              </Typography>
              <Typography variant={{ xs: "h5", sm: "h4" }} sx={{ fontWeight: 600 }}>
                {data.total}
              </Typography>
            </CardContent>
          </Card>
          <Card sx={{ flex: 1, minWidth: { xs: 140, sm: 200 }, borderRadius: 2 }}>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Total Income
              </Typography>
              <Typography variant={{ xs: "h5", sm: "h4" }} color="success.main" sx={{ fontWeight: 600 }}>
                {formatCurrency(data.items.reduce((sum, i) => sum + i.amount, 0))}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Table */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer sx={{ overflowX: 'auto', maxWidth: '100%' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ minWidth: 100 }}>Date</TableCell>
                  <TableCell sx={{ minWidth: 100 }}>Source</TableCell>
                  <TableCell sx={{ minWidth: 150 }}>Description</TableCell>
                  <TableCell align="right" sx={{ minWidth: 100 }}>Amount</TableCell>
                  <TableCell align="center" sx={{ minWidth: 100 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.items.map((income) => (
                  <TableRow key={income._id} hover>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>{income.date}</TableCell>
                    <TableCell>
                      <Chip
                        label={income.source}
                        size="small"
                        sx={{
                          backgroundColor: alpha(theme.palette.success.main, 0.1),
                          color: theme.palette.success.main,
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' }, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{income.description || "-"}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600, color: theme.palette.success.main, fontSize: { xs: '0.75rem', sm: '0.875rem' } }}>
                      {formatCurrency(income.amount)}
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleEdit(income)}>
                          <Edit fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDelete(income)} color="error">
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {data && data.total_pages > 1 && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
              <Pagination
                count={data.total_pages}
                page={page}
                onChange={(_, value) => setPage(value)}
                color="primary"
                size={isMobile ? "small" : "medium"}
              />
            </Box>
          )}

          {data?.items.length === 0 && (
            <Box sx={{ textAlign: "center", py: 4, px: 2 }}>
              <Typography variant="body2" color="text.secondary">
                No income records found. Add your first income to get started.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Income</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 2 }}>
            <TextField
              label="Amount"
              type="number"
              fullWidth
              value={editForm.amount}
              onChange={(e) => setEditForm({ ...editForm, amount: e.target.value })}
              inputProps={{ step: "0.01", min: 0 }}
            />
            <TextField
              label="Date"
              type="date"
              fullWidth
              value={editForm.date}
              onChange={(e) => setEditForm({ ...editForm, date: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <FormControl fullWidth>
              <InputLabel>Source</InputLabel>
              <Select
                value={editForm.source}
                label="Source"
                onChange={(e) => setEditForm({ ...editForm, source: e.target.value })}
              >
                {INCOME_SOURCES.map((source) => (
                  <MenuItem key={source} value={source}>
                    {source}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={2}
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
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
        <DialogTitle>Delete Income</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this income record of{" "}
            <strong>{selected && formatCurrency(selected.amount)}</strong>?
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

export default Income;
