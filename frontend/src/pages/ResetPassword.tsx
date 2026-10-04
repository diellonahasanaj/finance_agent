import { useState, useEffect, type FormEvent, type ChangeEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress,
  Link,
  useTheme,
  alpha,
  InputAdornment,
  IconButton
} from '@mui/material';
import { 
  Lock as LockIcon, 
  Visibility,
  VisibilityOff,
  ArrowBack,
  CheckCircle
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import AuthCard from '../components/auth/AuthCard';
import API from '../services/api';

interface FormErrors {
  password?: string;
  confirmPassword?: string;
}

interface ResetPasswordForm {
  password: string;
  confirmPassword: string;
}

function ResetPassword() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [formData, setFormData] = useState<ResetPasswordForm>({ 
    password: '', 
    confirmPassword: '' 
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
      setTokenValid(false);
    } else {
      // Validate token
      validateToken();
    }
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await API.post('/auth/validate-reset-token', { token });
      setTokenValid(response.data.valid);
    } catch (err) {
      setTokenValid(false);
      setError('Invalid or expired reset link. Please request a new password reset.');
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, a number, and a special character';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await API.post('/auth/reset-password', { 
        token: token!,
        new_password: formData.password 
      });
      
      if (response.data.success) {
        setSuccess(true);
      } else {
        setError(response.data.message || 'Failed to reset password');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  if (tokenValid === false) {
    return (
      <AuthCard 
        title="Invalid Link"
        subtitle="The password reset link is invalid or expired"
        icon={<LockIcon />}
      >
        <Box sx={{ width: '100%', maxWidth: 400, textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
          
          <Button
            fullWidth
            variant="outlined"
            onClick={() => navigate('/forgot-password')}
            sx={{ 
              py: 2,
              textTransform: 'none',
              fontSize: '1rem',
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            Request New Reset Link
          </Button>
        </Box>
      </AuthCard>
    );
  }

  if (tokenValid === null) {
    return (
      <AuthCard 
        title="Validating..."
        subtitle="Please wait while we validate your reset link"
        icon={<LockIcon />}
      >
        <Box sx={{ width: '100%', maxWidth: 400, textAlign: 'center' }}>
          <CircularProgress />
        </Box>
      </AuthCard>
    );
  }

  return (
    <AuthCard 
      title="Reset Password"
      subtitle="Enter your new password"
      icon={<LockIcon />}
    >
      <Box sx={{ width: '100%', maxWidth: 400 }}>
        {/* Success Message */}
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Alert 
              severity="success" 
              sx={{ mb: 3 }}
              icon={<CheckCircle />}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Password reset successful!
              </Typography>
              <Typography variant="body2">
                Your password has been updated. You can now sign in with your new password.
              </Typography>
            </Alert>
          </motion.div>
        )}

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          </motion.div>
        )}

        {!success ? (
          <form onSubmit={handleSubmit}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <TextField
                fullWidth
                label="New Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
                disabled={loading}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: <LockIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={togglePasswordVisibility}
                        edge="end"
                        disabled={loading}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <TextField
                fullWidth
                label="Confirm New Password"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword}
                disabled={loading}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: <LockIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={toggleConfirmPasswordVisibility}
                        edge="end"
                        disabled={loading}
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ 
                  py: 2,
                  textTransform: 'none',
                  fontSize: '1rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                  boxShadow: `0 4px 14px ${alpha(theme.palette.primary.main, 0.3)}`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                    boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
                    transform: 'translateY(-1px)',
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Reset Password'
                )}
              </Button>
            </motion.div>
          </form>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Button
              fullWidth
              variant="contained"
              onClick={() => navigate('/login')}
              sx={{ 
                py: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
                borderRadius: 2,
              }}
            >
              Sign In
            </Button>
          </motion.div>
        )}

        {/* Back to Login Link */}
        {!success && (
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <Link 
                component="button" 
                variant="body2" 
                onClick={() => navigate('/login')}
                sx={{ 
                  fontWeight: 600,
                  color: theme.palette.primary.main,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
                type="button"
              >
                <ArrowBack sx={{ fontSize: 16 }} />
                Back to Sign In
              </Link>
            </motion.div>
          </Box>
        )}
      </Box>
    </AuthCard>
  );
}

export default ResetPassword;
