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
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  MenuItem,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import { Logout as LogoutIcon, Delete as DeleteIcon } from '@mui/icons-material';
import API from '../services/api';

interface SettingsProps {
  onLogout: () => void;
}

interface UserProfile {
  _id: string;
  name: string;
  email: string;
  monthly_income?: number;
  savings_goal?: number;
  currency?: string;
}

const CURRENCIES = ['USD', 'EUR', 'GBP', 'CHF', 'PLN'];

const Settings: React.FC<SettingsProps> = ({ onLogout }) => {
  const theme = useTheme();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [notifications, setNotifications] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const [profileForm, setProfileForm] = useState({
    name: '',
    monthly_income: '',
    savings_goal: '',
    currency: 'USD',
  });

  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const loadProfile = async () => {
    try {
      const response = await API.get('/auth/me');
      const profile = response.data;
      setUser(profile);
      localStorage.setItem('user', JSON.stringify(profile));
      if (profile.currency) localStorage.setItem('currency', profile.currency);
      setProfileForm({
        name: profile.name || '',
        monthly_income: profile.monthly_income != null ? String(profile.monthly_income) : '',
        savings_goal: profile.savings_goal != null ? String(profile.savings_goal) : '',
        currency: profile.currency || 'USD',
      });
    } catch {
      const userData = localStorage.getItem('user');
      if (userData) setUser(JSON.parse(userData));
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    onLogout();
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    try {
      const payload: Record<string, string | number> = { name: profileForm.name, currency: profileForm.currency };
      if (profileForm.monthly_income) payload.monthly_income = parseFloat(profileForm.monthly_income);
      if (profileForm.savings_goal) payload.savings_goal = parseFloat(profileForm.savings_goal);

      const response = await API.put('/auth/profile', payload);
      const updated = response.data.user;
      setUser(updated);
      localStorage.setItem('user', JSON.stringify(updated));
      if (updated.currency) localStorage.setItem('currency', updated.currency);
      setProfileDialogOpen(false);
      setSnackbar({ open: true, message: 'Profile updated successfully', severity: 'success' });
    } catch (err: any) {
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Failed to update profile', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setSnackbar({ open: true, message: 'Passwords do not match', severity: 'error' });
      return;
    }
    setLoading(true);
    try {
      await API.post('/auth/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      setPasswordDialogOpen(false);
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      setSnackbar({ open: true, message: 'Password changed successfully', severity: 'success' });
    } catch (err: any) {
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Failed to change password', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteData = async () => {
    if (deleteConfirm !== 'DELETE') return;
    try {
      await API.delete('/finance/privacy/delete-data');
      setSnackbar({ open: true, message: 'All financial data deleted', severity: 'success' });
      setDeleteDialogOpen(false);
      setDeleteConfirm('');
    } catch {
      setSnackbar({ open: true, message: 'Failed to delete data', severity: 'error' });
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>Settings</Typography>
        <Typography variant="body1" color="textSecondary">
          Manage your account and application preferences
        </Typography>
      </Box>

      <Stack spacing={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Profile Information</Typography>
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">Name</Typography>
                <Typography variant="body1">{user?.name || 'Unknown'}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">Email</Typography>
                <Typography variant="body1">{user?.email || 'Unknown'}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">Monthly Income Target</Typography>
                <Typography variant="body1">
                  {user?.monthly_income != null ? `${user.currency || 'USD'} ${user.monthly_income}` : 'Not set'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">Savings Goal</Typography>
                <Typography variant="body1">
                  {user?.savings_goal != null ? `${user.currency || 'USD'} ${user.savings_goal}` : 'Not set (defaults to 20% of income)'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">Currency</Typography>
                <Typography variant="body1">{user?.currency || 'USD'}</Typography>
              </Box>
              <Button variant="outlined" size="small" sx={{ width: 'fit-content' }} onClick={() => setProfileDialogOpen(true)}>
                Edit Profile
              </Button>
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Notifications</Typography>
            <Stack spacing={2}>
              <FormControlLabel
                control={<Switch checked={notifications} onChange={(e) => setNotifications(e.target.checked)} />}
                label="Push Notifications"
              />
              <FormControlLabel
                control={<Switch checked={emailAlerts} onChange={(e) => setEmailAlerts(e.target.checked)} />}
                label="Email Alerts for Budget Warnings"
              />
            </Stack>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Security</Typography>
            <Button variant="outlined" size="small" sx={{ width: 'fit-content' }} onClick={() => setPasswordDialogOpen(true)}>
              Change Password
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>Session</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Logged in as <strong>{user?.email}</strong>
            </Typography>
            <Button variant="contained" color="primary" startIcon={<LogoutIcon />} onClick={handleLogout}>
              Logout
            </Button>
          </CardContent>
        </Card>

        <Card sx={{ borderColor: theme.palette.error.main, border: 2 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: theme.palette.error.main }}>
              Danger Zone
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Permanently delete all your financial data (transactions, budgets, recommendations).
            </Typography>
            <Button variant="outlined" color="error" startIcon={<DeleteIcon />} onClick={() => setDeleteDialogOpen(true)}>
              Delete All Financial Data
            </Button>
          </CardContent>
        </Card>
      </Stack>

      <Dialog open={profileDialogOpen} onClose={() => setProfileDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Name" value={profileForm.name} onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })} fullWidth />
            <TextField label="Monthly Income Target" type="number" value={profileForm.monthly_income} onChange={(e) => setProfileForm({ ...profileForm, monthly_income: e.target.value })} fullWidth />
            <TextField label="Savings Goal" type="number" value={profileForm.savings_goal} onChange={(e) => setProfileForm({ ...profileForm, savings_goal: e.target.value })} fullWidth helperText="Used for savings progress on the dashboard" />
            <TextField select label="Currency" value={profileForm.currency} onChange={(e) => setProfileForm({ ...profileForm, currency: e.target.value })} fullWidth>
              {CURRENCIES.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveProfile} disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={passwordDialogOpen} onClose={() => setPasswordDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Current Password" type="password" value={passwordForm.current_password} onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })} fullWidth />
            <TextField label="New Password" type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} fullWidth helperText="Min 8 chars, uppercase, lowercase, number, special character" />
            <TextField label="Confirm New Password" type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })} fullWidth />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleChangePassword} disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Change Password'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete All Financial Data</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>This cannot be undone. Your account will remain but all transactions and budgets will be removed.</Alert>
          <Typography variant="body2" sx={{ mb: 2 }}>Type <strong>DELETE</strong> to confirm:</Typography>
          <TextField fullWidth value={deleteConfirm} onChange={(e) => setDeleteConfirm(e.target.value)} placeholder="Type DELETE" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" onClick={handleDeleteData} disabled={deleteConfirm !== 'DELETE'}>Delete Data</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })} message={snackbar.message} />
    </Container>
  );
};

export default Settings;
