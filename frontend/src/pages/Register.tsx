

import API from "../services/api";
import { 
  TextField, 
  Button, 
  Typography, 
  Alert, 
  Link, 
  InputAdornment, 
  IconButton, 
  CircularProgress, 
  Box,
  LinearProgress,
  useTheme,
  alpha,
  Divider
} from '@mui/material';
import type { FormEvent, ChangeEvent } from "react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Visibility, 
  VisibilityOff, 
  Email as EmailIcon, 
  Lock as LockIcon, 
  Person as PersonIcon, 
  CheckCircle, 
  Cancel,
  Google,
  GitHub
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import AuthCard from '../components/auth/AuthCard';

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

interface PasswordCheck {
  regex: RegExp;
  text: string;
  met: boolean;
}

interface RegisterForm {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface RegisterProps {
  onRegister?: () => void;
}

function Register({ onRegister }: RegisterProps) {
  const theme = useTheme();
  const [form, setForm] = useState<RegisterForm>({ name: "", email: "", password: "", confirmPassword: "" });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, feedback: [] as string[] });
  const navigate = useNavigate();

  const passwordRequirements: PasswordCheck[] = [
    { regex: /[A-Z]/, text: "One uppercase letter", met: false },
    { regex: /[a-z]/, text: "One lowercase letter", met: false },
    { regex: /\d/, text: "One number", met: false },
    { regex: /[!@#$%^&*(),.?":{}|<>]/, text: "One special character", met: false },
    { regex: /.{8,}/, text: "At least 8 characters", met: false }
  ];

  const [passwordChecks, setPasswordChecks] = useState<PasswordCheck[]>(passwordRequirements);

  useEffect(() => {
    const checks = passwordRequirements.map(req => ({
      ...req,
      met: req.regex.test(form.password)
    }));
    setPasswordChecks(checks);
    
    const score = checks.filter(check => check.met).length;
    setPasswordStrength({ 
      score, 
      feedback: checks.filter(check => !check.met).map(check => check.text) 
    });
  }, [form.password]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    
    // Clear field error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors({ ...errors, [name]: "" });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!form.name) {
      newErrors.name = "Name is required";
    } else if (form.name.length < 2) {
      newErrors.name = "Name must be at least 2 characters";
    } else if (form.name.length > 100) {
      newErrors.name = "Name must be less than 100 characters";
    } else if (!/^[a-zA-Z\s\-\.]+$/.test(form.name)) {
      newErrors.name = "Name can only contain letters, spaces, hyphens, and periods";
    }
    
    if (!form.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(form.email)) {
      newErrors.email = "Email is invalid";
    }
    
    if (!form.password) {
      newErrors.password = "Password is required";
    } else if (passwordStrength.score < 5) {
      newErrors.password = "Password does not meet all requirements";
    }
    
    if (!form.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const res = await API.post("/auth/register", {
        name: form.name,
        email: form.email,
        password: form.password
      });
      
      if (res.data.success) {
        if (onRegister) {
          onRegister();
        }
        
        // Show success message and redirect to login
        setError("");
        navigate('/login', { 
          state: { 
            message: "Registration successful! Please check your email to verify your account." 
          } 
        });
      } else {
        setError(res.data.message || "Registration failed");
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 
                          err.response?.data?.detail || 
                          "Registration failed. Please try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength.score <= 2) return theme.palette.error.main;
    if (passwordStrength.score <= 3) return theme.palette.warning.main;
    if (passwordStrength.score <= 4) return theme.palette.info.main;
    return theme.palette.success.main;
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength.score <= 2) return "Weak";
    if (passwordStrength.score <= 3) return "Fair";
    if (passwordStrength.score <= 4) return "Good";
    return "Strong";
  };

  return (
    <AuthCard
      title="Create Account"
      subtitle="Join Personal Finance to manage your money smarter"
      icon={<PersonIcon />}
    >
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Alert severity="error" sx={{ borderRadius: 2 }}>
              {error}
            </Alert>
          </motion.div>
        )}

        {/* Social Login Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ flex: 1 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Google />}
              sx={{
                py: 1.5,
                borderColor: alpha(theme.palette.divider, 0.3),
                color: theme.palette.text.secondary,
                '&:hover': {
                  borderColor: theme.palette.primary.main,
                  backgroundColor: alpha(theme.palette.primary.main, 0.04),
                },
              }}
            >
              Google
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ flex: 1 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<GitHub />}
              sx={{
                py: 1.5,
                borderColor: alpha(theme.palette.divider, 0.3),
                color: theme.palette.text.secondary,
                '&:hover': {
                  borderColor: theme.palette.primary.main,
                  backgroundColor: alpha(theme.palette.primary.main, 0.04),
                },
              }}
            >
              GitHub
            </Button>
          </motion.div>
        </Box>

        <Divider sx={{ my: 1 }}>
          <Typography variant="body2" color="text.secondary">
            OR
          </Typography>
        </Divider>

        {/* Name Field */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <TextField
            name="name"
            label="Full Name"
            value={form.name}
            onChange={handleChange}
            required
            fullWidth
            error={!!errors.name}
            helperText={errors.name}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <PersonIcon color="action" />
                </InputAdornment>
              ),
            }}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused': {
                  boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`,
                },
              },
            }}
          />
        </motion.div>
        
        {/* Email Field */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <TextField
            name="email"
            type="email"
            label="Email Address"
            value={form.email}
            onChange={handleChange}
            required
            fullWidth
            error={!!errors.email}
            helperText={errors.email}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon color="action" />
                </InputAdornment>
              ),
            }}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused': {
                  boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`,
                },
              },
            }}
          />
        </motion.div>
        
        {/* Password Field */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <TextField
            name="password"
            type={showPassword ? "text" : "password"}
            label="Password"
            value={form.password}
            onChange={handleChange}
            required
            fullWidth
            error={!!errors.password}
            helperText={errors.password}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                    disabled={loading}
                    sx={{
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.action.hover, 0.08),
                      },
                    }}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused': {
                  boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`,
                },
              },
            }}
          />
        </motion.div>
        
        {/* Password Strength Indicator */}
        {form.password && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ mt: 1, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="caption" sx={{ mr: 1, color: theme.palette.text.secondary }}>
                  Password strength:
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontWeight: 'bold',
                    color: getPasswordStrengthColor()
                  }}
                >
                  {getPasswordStrengthText()}
                </Typography>
              </Box>
              
              {/* Progress Bar */}
              <Box sx={{ width: '100%', mb: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={(passwordStrength.score / 5) * 100}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: alpha(theme.palette.divider, 0.2),
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getPasswordStrengthColor(),
                      borderRadius: 2,
                    },
                  }}
                />
              </Box>
              
              {/* Requirements */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                {passwordChecks.map((check, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    style={{ display: 'flex', alignItems: 'center' }}
                  >
                    {check.met ? (
                      <CheckCircle 
                        sx={{ 
                          fontSize: 16, 
                          color: theme.palette.success.main, 
                          mr: 1 
                        }} 
                      />
                    ) : (
                      <Cancel 
                        sx={{ 
                          fontSize: 16, 
                          color: theme.palette.error.main, 
                          mr: 1 
                        }} 
                      />
                    )}
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: check.met ? theme.palette.success.main : theme.palette.error.main,
                        fontSize: '0.75rem'
                      }}
                    >
                      {check.text}
                    </Typography>
                  </motion.div>
                ))}
              </Box>
            </Box>
          </motion.div>
        )}
        
        {/* Confirm Password Field */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <TextField
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            label="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            required
            fullWidth
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle confirm password visibility"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    edge="end"
                    disabled={loading}
                    sx={{
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.action.hover, 0.08),
                      },
                    }}
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused': {
                  boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.1)}`,
                },
              },
            }}
          />
        </motion.div>

        {/* Submit Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Button 
            type="submit" 
            variant="contained" 
            size="large"
            disabled={loading || passwordStrength.score < 5}
            fullWidth
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
              '&:disabled': {
                background: theme.palette.action.disabled,
                boxShadow: 'none',
              },
            }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Create Account'
            )}
          </Button>
        </motion.div>

        {/* Sign In Link */}
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Link 
                component="button" 
                variant="body2" 
                onClick={() => navigate('/login')}
                sx={{ 
                  fontWeight: 600,
                  color: theme.palette.primary.main,
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
                type="button"
              >
                Sign in here
              </Link>
            </Typography>
          </motion.div>
        </Box>
      </Box>
    </AuthCard>
  );
}

export default Register;
