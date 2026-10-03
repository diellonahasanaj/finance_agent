import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Divider,
  IconButton,
  useMediaQuery,
  useTheme,
  AppBar,
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
  ListAlt,
  Settings,
  AccountBalanceWallet,
  CreditCard,
  CloudUpload,
  Menu as MenuIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";

const DRAWER_WIDTH = 260;

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: <Dashboard /> },
  { label: "Transactions", path: "/transactions", icon: <ListAlt /> },
  { label: "Income", path: "/income", icon: <AccountBalanceWallet /> },
  { label: "Debt", path: "/debt", icon: <CreditCard /> },
  { label: "Add Transaction", path: "/add-transaction", icon: <AddCircle /> },
  { label: "Set Budget", path: "/set-budget", icon: <AccountBalance /> },
  { label: "Data Management", path: "/data-management", icon: <CloudUpload /> },
  { label: "Reports", path: "/reports", icon: <Assessment /> },
  { label: "Recommendations", path: "/recommendations", icon: <Lightbulb /> },
  { label: "Analytics", path: "/analytics", icon: <Analytics /> },
  { label: "Advisor", path: "/advisor", icon: <Chat /> },
  { label: "Transparency", path: "/transparency", icon: <Visibility /> },
  { label: "Settings", path: "/settings", icon: <Settings /> },
];

interface SideBarProps {
  mobileOpen?: boolean;
  onDrawerToggle?: () => void;
}

function SideBar({ mobileOpen, onDrawerToggle }: SideBarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const drawer = (
    <>
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
            onClick={() => {
              navigate(item.path);
              if (isMobile && onDrawerToggle) {
                onDrawerToggle();
              }
            }}
          >
            <ListItemIcon sx={{ color: "inherit", minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </>
  );

  return (
    <>
      {/* Mobile AppBar with hamburger menu */}
      {isMobile && (
        <AppBar
          position="fixed"
          sx={{
            width: '100%',
            ml: 0,
            zIndex: theme.zIndex.drawer + 1,
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={onDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Finance Advisor
            </Typography>
          </Toolbar>
        </AppBar>
      )}

      {/* Sidebar - permanent on desktop, temporary on mobile */}
      <Drawer
        variant={isMobile ? "temporary" : "permanent"}
        open={isMobile ? mobileOpen : true}
        onClose={onDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            ...(isMobile && {
              top: 0,
              height: '100%',
            }),
          },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
}

export default SideBar;
