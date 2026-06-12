import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Divider,
} from "@mui/material";
import {
  Dashboard,
  AddCircle,
  AccountBalance,
  Assessment,
  Lightbulb,
  Analytics,
  Chat,
  Visibility,
  Settings,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";

const DRAWER_WIDTH = 260;

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: <Dashboard /> },
  { label: "Add Expense", path: "/add-expense", icon: <AddCircle /> },
  { label: "Add Transaction", path: "/add-transaction", icon: <AddCircle /> },
  { label: "Set Budget", path: "/set-budget", icon: <AccountBalance /> },
  { label: "Reports", path: "/reports", icon: <Assessment /> },
  { label: "Recommendations", path: "/recommendations", icon: <Lightbulb /> },
  { label: "Analytics", path: "/analytics", icon: <Analytics /> },
  { label: "Advisor", path: "/advisor", icon: <Chat /> },
  { label: "Transparency", path: "/transparency", icon: <Visibility /> },
  { label: "Settings", path: "/settings", icon: <Settings /> },
];

interface SideBarProps {
  darkMode: boolean;
  onDarkModeChange: (value: boolean) => void;
}

function SideBar({ darkMode, onDarkModeChange }: SideBarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
        },
      }}
    >
      <Toolbar>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: "white" }}>
            Finance Advisor
          </Typography>
          <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)" }}>
            Personal Finance Agent
          </Typography>
        </Box>
      </Toolbar>
      <Divider sx={{ borderColor: "rgba(255,255,255,0.12)" }} />
      <List sx={{ flex: 1, px: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
          >
            <ListItemIcon sx={{ color: "inherit", minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Box sx={{ p: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={darkMode}
              onChange={(e) => onDarkModeChange(e.target.checked)}
              color="default"
            />
          }
          label={
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
              Dark mode
            </Typography>
          }
        />
      </Box>
    </Drawer>
  );
}

export default SideBar;
