import { useState, useCallback } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  useTheme,
  alpha,
} from "@mui/material";
import {
  CloudUpload,
  Download,
  ArrowBack,
  FileUpload,
  Description,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function DataManagement() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importType, setImportType] = useState("expenses");
  const [importFormat, setImportFormat] = useState("json");

  const handleExport = async (dataType: string, format: string) => {
    try {
      setLoading(true);
      const response = await API.get(`/finance/export/${format}`, {
        params: { data_type: dataType },
        responseType: format === "json" ? "json" : "blob",
      });

      if (format === "json") {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], {
          type: "application/json",
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${dataType}_export.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = `${dataType}_export.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
      }

      setSuccess(`${dataType.toUpperCase()} exported successfully as ${format.toUpperCase()}`);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to export data");
    } finally {
      setLoading(false);
    }
  };

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

  const exportOptions = [
    { type: "expenses", label: "Expenses", icon: <Description /> },
    { type: "income", label: "Income", icon: <Description /> },
    { type: "budgets", label: "Budgets", icon: <Description /> },
    { type: "debts", label: "Debts", icon: <Description /> },
  ];

  const importTypes = [
    { value: "expenses", label: "Expenses" },
    { value: "income", label: "Income" },
    { value: "budgets", label: "Budgets" },
    { value: "debts", label: "Debts" },
  ];

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
        <Box>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/settings")}
            sx={{ mb: 2 }}
          >
            Back to Settings
          </Button>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
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
        <CardContent>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ borderBottom: 1, borderColor: "divider" }}
          >
            <Tab label="Export Data" />
            <Tab label="Import Data" />
          </Tabs>

          {/* Export Tab */}
          <TabPanel value={tabValue} index={0}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Export Your Data
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Download your financial data in JSON or CSV format for backup or analysis.
            </Typography>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Data Type</TableCell>
                    <TableCell>Export as JSON</TableCell>
                    <TableCell>Export as CSV</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {exportOptions.map((option) => (
                    <TableRow key={option.type}>
                      <TableCell>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                          {option.icon}
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {option.label}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Button
                          startIcon={<Download />}
                          variant="outlined"
                          size="small"
                          onClick={() => handleExport(option.type, "json")}
                          disabled={loading}
                        >
                          JSON
                        </Button>
                      </TableCell>
                      <TableCell>
                        <Button
                          startIcon={<Download />}
                          variant="outlined"
                          size="small"
                          onClick={() => handleExport(option.type, "csv")}
                          disabled={loading}
                        >
                          CSV
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Tip:</strong> JSON format preserves all data fields and is recommended for backups.
                CSV format is better for spreadsheet analysis but may lose some complex data structures.
              </Typography>
            </Alert>
          </TabPanel>

          {/* Import Tab */}
          <TabPanel value={tabValue} index={1}>
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
              <Box sx={{ minWidth: 200 }}>
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

              <Box sx={{ minWidth: 200 }}>
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
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}

export default DataManagement;
