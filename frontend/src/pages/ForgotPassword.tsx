import { useState, type FormEvent, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Alert, 
  CircularProgress,
  Link,
  useTheme,
  alpha
} from '@mui/material';
import { 
  Email as EmailIcon, 
  ArrowBack,
  CheckCircle
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import AuthCard from '../components/auth/AuthCard';
import API from '../services/api';

interface FormErrors {
  email?: string;
}

interface ForgotPasswordForm {
  email: string;
}

function ForgotPassword() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<ForgotPasswordForm>({ email: '' });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState<any>(null);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
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
      const response = await API.post('/auth/forgot-password', { email: formData.email });
      
      if (response.data.success) {
        setSuccess(true);
        setDebugInfo(response.data.debug_info);
      } else {
        setError(response.data.message || 'Failed to send reset email');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.');
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

  return (
    <AuthCard 
      title="Forgot Password"
      subtitle="Enter your email to reset your password"
      icon={<EmailIcon />}
    >
      <Box sx={{ width: '100%', maxWidth: 400 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
              boxShadow: `0 4px 14px ${alpha(theme.palette.primary.main, 0.3)}`
            }}>
              <EmailIcon sx={{ fontSize: 30, color: 'white' }} />
            </Box>
          </motion.div>
          
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Forgot Password
          </Typography>
          
          <Typography variant="body2" color="text.secondary">
            Enter your email address and we'll send you a link to reset your password
          </Typography>
        </Box>

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
                Password reset email sent!
              </Typography>
              <Typography variant="body2">
                Check your inbox for {formData.email} and follow the instructions to reset your password.
              </Typography>
              
              {/* Debug Information */}
              {debugInfo && (
                <Box sx={{ mt: 2, p: 2, backgroundColor: 'rgba(0,0,0,0.05)', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Demo Mode - Email Simulation:
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                    Reset Link: <a href={debugInfo.reset_link} target="_blank" rel="noopener noreferrer" style={{ color: theme.palette.primary.main }}>
                      Click here to reset password
                    </a>
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                    Token: {debugInfo.token}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                    Expires: {new Date(debugInfo.expires_at).toLocaleString()}
                  </Typography>
                </Box>
              )}
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
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!errors.email}
                helperText={errors.email}
                disabled={loading}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
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
                  'Send Reset Email'
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
              variant="outlined"
              onClick={() => navigate('/login')}
              sx={{ 
                py: 2,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
                borderRadius: 2,
              }}
            >
              Back to Sign In
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

export default ForgotPassword;
