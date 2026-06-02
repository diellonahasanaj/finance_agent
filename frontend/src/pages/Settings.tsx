import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
} from '@mui/material';
import { Exit as LogoutIcon, Delete as DeleteIcon } from '@mui/icons-material';
// @ts-ignore
import API from '../services/api';

interface SettingsProps {
  onLogout: () => void;
}

const Settings: React.FC<SettingsProps> = ({ onLogout }) => {
  const theme = useTheme();
  const [user, setUser] = useState<any>(null);
  const [notifications, setNotifications] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    onLogout();
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirm !== 'DELETE') {
      alert('Please type DELETE to confirm');
      return;
    }

    try {
      await API.post('/auth/delete-account');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      onLogout();
    } catch (error) {
      alert('Failed to delete account');
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Manage your account and application preferences
        </Typography>
      </Box>

      <Stack spacing={3}>
        {/* Profile Section */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Profile Information
            </Typography>
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">
                  Name
                </Typography>
                <Typography variant="body1">{user?.name || 'Unknown'}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">
                  Email
                </Typography>
                <Typography variant="body1">{user?.email || 'Unknown'}</Typography>
              </Box>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }}>
                Edit Profile
              </Button>
            </Stack>
          </CardContent>
        </Card>

        <Divider />

        {/* Notification Settings */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Notifications
            </Typography>
            <Stack spacing={2}>
              <FormControlLabel
                control={<Switch checked={notifications} onChange={(e) => setNotifications(e.target.checked)} />}
                label="Push Notifications"
              />
              <FormControlLabel
                control={<Switch checked={emailAlerts} onChange={(e) => setEmailAlerts(e.target.checked)} />}
                label="Email Alerts for Budget Warnings"
              />
              <Typography variant="caption" color="textSecondary">
                You can customize these notifications in your notification preferences.
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        {/* Security Section */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Security
            </Typography>
            <Stack spacing={2}>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }}>
                Change Password
              </Button>
              <Typography variant="caption" color="textSecondary">
                For your security, we recommend changing your password regularly.
              </Typography>
            </Stack>
          </CardContent>
        </Card>

        <Divider />

        {/* Session Section */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Session
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              You are currently logged in as <strong>{user?.email}</strong>
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
            >
              Logout
            </Button>
          </CardContent>
        </Card>

        <Divider />

        {/* Danger Zone */}
        <Card sx={{ borderColor: theme.palette.error.main, border: 2 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: theme.palette.error.main }}>
              Danger Zone
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              These actions cannot be undone. Please proceed with caution.
            </Typography>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete Account
            </Button>
          </CardContent>
        </Card>

        {/* Data & Privacy */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Data & Privacy
            </Typography>
            <Stack spacing={1}>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }}>
                Download My Data
              </Button>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }}>
                Privacy Policy
              </Button>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }}>
                Terms of Service
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Stack>

      {/* Delete Account Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Account</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This action cannot be undone. All your data will be permanently deleted.
          </Alert>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Type <strong>DELETE</strong> to confirm:
          </Typography>
          <TextField
            fullWidth
            value={deleteConfirm}
            onChange={(e) => setDeleteConfirm(e.target.value)}
            placeholder="Type DELETE"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            color="error"
            onClick={handleDeleteAccount}
            disabled={deleteConfirm !== 'DELETE'}
          >
            Delete Account
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Settings;
