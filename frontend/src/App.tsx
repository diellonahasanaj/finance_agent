// src/App.tsx
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Box, CssBaseline, Toolbar, ThemeProvider } from "@mui/material";
import { useState, useEffect } from "react";

import Dashboard from "./pages/Dashboard";
import AddExpense from "./pages/AddExpense";
import AddTransaction from "./pages/AddTransaction";
import SetBudget from "./pages/SetBudget";
import Reports from "./pages/Reports";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

import SideBar from "./components/layout/SideBar";
import theme from "./theme/theme";

// Define type for a user
interface User {
  _id: string;
  name: string;
  email: string;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const location = useLocation();

  // Check if user is logged in (token in localStorage)
  useEffect(() => {
    console.log("🔍 Checking authentication...");
    const token = localStorage.getItem("token");
    console.log("🔑 Token found:", !!token);
    
    let foundUser: User | null = null;

    if (token) {
      try {
        const userData = localStorage.getItem("user");
        console.log("👤 User data found:", !!userData);
        if (userData) {
          foundUser = JSON.parse(userData);
          console.log("✅ Parsed user:", foundUser);
        }
      } catch (error) {
        console.error("❌ Error parsing user data:", error);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }

    // Set auth state immediately without timeout
    console.log("🚀 Setting auth state:", { user: foundUser, authChecked: true });
    setUser(foundUser);
    setAuthChecked(true);
  }, []);

  // Handle registration success message
  useEffect(() => {
    const state = location.state as any;
    if (state?.message) {
      // You could show a toast notification here
      console.log("📧 Registration message:", state.message);
      // Clear the state to prevent showing the message again
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Always render something, even during auth check
  console.log("🎨 Rendering App with user:", user, "authChecked:", authChecked);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "flex" }}>
        {/* Sidebar only visible if user is logged in */}
        {user && <SideBar />}

        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Routes>
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
            <Route path="/login" element={<Login onLogin={(user) => setUser(user)} />} />
            <Route path="/register" element={<Register onRegister={() => {}} />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
            <Route path="/add-expense" element={user ? <AddExpense /> : <Navigate to="/login" />} />
            <Route path="/add-transaction" element={user ? <AddTransaction /> : <Navigate to="/login" />} />
            <Route path="/set-budget" element={user ? <SetBudget /> : <Navigate to="/login" />} />
            <Route path="/reports" element={user ? <Reports /> : <Navigate to="/login" />} />
            <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;