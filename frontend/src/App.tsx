// src/App.tsx
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Box, CssBaseline, Toolbar, ThemeProvider, createTheme, useMediaQuery, useTheme as useMuiTheme } from "@mui/material";
import { useState, useEffect } from "react";

import Dashboard from "./pages/Dashboard";
import AddExpense from "./pages/AddExpense";
import AddTransaction from "./pages/AddTransaction";
import SetBudget from "./pages/SetBudget";
import Reports from "./pages/Reports";
import Recommendations from "./pages/Recommendations";
import Analytics from "./pages/Analytics";
import Advisor from "./pages/Advisor";
import Transparency from "./pages/Transparency";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Settings from "./pages/Settings";
import Transactions from "./pages/Transactions";
import Income from "./pages/Income";
import Debt from "./pages/Debt";
import DataManagement from "./pages/DataManagement";

import SideBar from "./components/layout/SideBar";

// Define type for a user
interface User {
  _id: string;
  name: string;
  email: string;
}

// Dark mode theme (permanent)
const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#1976d2" },
    secondary: { main: "#dc004e" },
    background: { default: "#121212", paper: "#1e1e1e" },
    success: { main: "#4caf50" },
    error: { main: "#f44336" },
    warning: { main: "#ff9800" },
    info: { main: "#2196f3" },
  },
});

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const theme = useMuiTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Check if user is logged in (token in localStorage)
  useEffect(() => {
    const token = localStorage.getItem("token");
    let foundUser: User | null = null;

    if (token) {
      try {
        const userData = localStorage.getItem("user");
        if (userData) {
          foundUser = JSON.parse(userData);
        }
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    setUser(foundUser);
  }, []);

  // Handle registration success message
  useEffect(() => {
    const state = location.state as { message?: string } | null;
    if (state?.message) {
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: "flex" }}>
        {/* Sidebar only visible if user is logged in */}
        {user && (
          <SideBar
            mobileOpen={mobileOpen}
            onDrawerToggle={handleDrawerToggle}
          />
        )}

        <Box component="main" sx={{ flexGrow: 1, width: { xs: '100%', md: user ? 'calc(100% - 260px)' : '100%' }, ml: { md: user ? '260px' : 0 } }}>
          {/* Add Toolbar for mobile to account for AppBar */}
          {user && isMobile && <Toolbar />}
          <Routes>
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
            <Route path="/login" element={<Login onLogin={(user) => setUser(user)} />} />
            <Route path="/register" element={<Register onRegister={() => {}} />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/add-expense" element={user ? <AddExpense /> : <Navigate to="/login" />} />
            <Route path="/add-transaction" element={user ? <AddTransaction /> : <Navigate to="/login" />} />
            <Route path="/transactions" element={user ? <Transactions /> : <Navigate to="/login" />} />
            <Route path="/income" element={user ? <Income /> : <Navigate to="/login" />} />
            <Route path="/debt" element={user ? <Debt /> : <Navigate to="/login" />} />
            <Route path="/data-management" element={user ? <DataManagement /> : <Navigate to="/login" />} />
            <Route path="/set-budget" element={user ? <SetBudget /> : <Navigate to="/login" />} />
            <Route path="/reports" element={user ? <Reports /> : <Navigate to="/login" />} />
            <Route path="/advisor" element={user ? <Advisor /> : <Navigate to="/login" />} />
            <Route path="/recommendations" element={user ? <Recommendations /> : <Navigate to="/login" />} />
            <Route path="/analytics" element={user ? <Analytics /> : <Navigate to="/login" />} />
            <Route path="/transparency" element={user ? <Transparency /> : <Navigate to="/login" />} />
            <Route path="/settings" element={user ? <Settings onLogout={() => setUser(null)} /> : <Navigate to="/login" />} />
            <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
