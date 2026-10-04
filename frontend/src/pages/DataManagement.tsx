import { useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  useTheme,
  alpha,
} from "@mui/material";
import {
  CloudUpload,
  ArrowBack,
  FileUpload,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function DataManagement() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importType, setImportType] = useState("expenses");
  const [importFormat, setImportFormat] = useState("json");

  const handleImport = async () => {
    if (!importFile) {
      setError("Please select a file to import");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("file", importFile);

      const endpoint =
        importFormat === "json"
          ? `/finance/import/json?data_type=${importType}`
          : `/finance/import/csv?data_type=${importType}`;

      await API.post(endpoint, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setSuccess(`${importType.toUpperCase()} imported successfully`);
      setImportFile(null);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to import data");
    } finally {
      setLoading(false);
    }
  };

  const importTypes = [
    { value: "expenses", label: "Expenses" },
    { value: "income", label: "Income" },
    { value: "budgets", label: "Budgets" },
    { value: "debts", label: "Debts" },
  ];

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
        <Box sx={{ minWidth: 0, flex: 1 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/settings")}
            sx={{ mb: 2 }}
          >
            Back to Settings
          </Button>
          <Typography variant="h4" sx={{ fontWeight: 600, fontSize: { xs: '1.75rem', sm: '2.125rem' } }}>
            Data Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Import and export your financial data
          </Typography>
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

      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Import Data
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload financial data from a JSON or CSV file. Make sure the file format matches the expected structure.
          </Typography>

          <Card
            sx={{
              p: 3,
              border: `2px dashed ${theme.palette.divider}`,
              borderRadius: 2,
              mb: 3,
              backgroundColor: alpha(theme.palette.primary.main, 0.02),
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 2,
              }}
            >
              <FileUpload sx={{ fontSize: 48, color: theme.palette.primary.main }} />
              <Typography variant="body2" color="text.secondary" textAlign="center">
                Drag and drop your file here, or click to select
              </Typography>
              <input
                type="file"
                accept={importFormat === "json" ? ".json" : ".csv"}
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                style={{ display: "none" }}
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUpload />}
                  disabled={loading}
                >
                  Select File
                </Button>
              </label>
              {importFile && (
                <Chip
                  label={importFile.name}
                  onDelete={() => setImportFile(null)}
                  color="primary"
                />
              )}
            </Box>
          </Card>

          <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
            <Box sx={{ minWidth: { xs: '100%', sm: 200 } }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                Data Type
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {importTypes.map((type) => (
                  <Chip
                    key={type.value}
                    label={type.label}
                    onClick={() => setImportType(type.value)}
                    color={importType === type.value ? "primary" : "default"}
                    variant={importType === type.value ? "filled" : "outlined"}
                    clickable
                  />
                ))}
              </Box>
            </Box>

            <Box sx={{ minWidth: { xs: '100%', sm: 200 } }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                File Format
              </Typography>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Chip
                  label="JSON"
                  onClick={() => setImportFormat("json")}
                  color={importFormat === "json" ? "primary" : "default"}
                  variant={importFormat === "json" ? "filled" : "outlined"}
                  clickable
                />
                <Chip
                  label="CSV"
                  onClick={() => setImportFormat("csv")}
                  color={importFormat === "csv" ? "primary" : "default"}
                  variant={importFormat === "csv" ? "filled" : "outlined"}
                  clickable
                />
              </Box>
            </Box>
          </Box>

          <Button
            variant="contained"
            size="large"
            onClick={handleImport}
            disabled={!importFile || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <FileUpload />}
            sx={{ minWidth: 200 }}
          >
            {loading ? "Importing..." : "Import Data"}
          </Button>

          <Alert severity="warning" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>Warning:</strong> Importing data will add to your existing records. Make sure to backup
              your current data before importing. Duplicate records may be created.
            </Typography>
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
}

export default DataManagement;
