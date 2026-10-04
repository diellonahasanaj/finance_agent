import React from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Avatar, 
  useTheme,
  alpha
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  AccountBalanceWallet,
  TrendingUp,
  Security
} from '@mui/icons-material';

interface AuthCardProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
}

const AuthCard: React.FC<AuthCardProps> = ({ 
  children, 
  title, 
  subtitle,
  icon
}) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        p: 2,
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 80%, ${alpha(theme.palette.primary.main, 0.1)} 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, ${alpha(theme.palette.secondary.main, 0.1)} 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, ${alpha(theme.palette.success.main, 0.05)} 0%, transparent 50%)
          `,
          zIndex: -1,
        }}
      />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ 
          duration: 0.6, 
          ease: 'easeOut',
          scale: { type: 'spring', stiffness: 100 }
        }}
        style={{ width: '100%', maxWidth: '480px' }}
      >
        <Paper
          elevation={24}
          sx={{
            p: { xs: 3, sm: 4 },
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            boxShadow: `
              0 20px 40px rgba(0, 0, 0, 0.1),
              0 0 0 1px rgba(255, 255, 255, 0.05),
              inset 0 1px 0 rgba(255, 255, 255, 0.1)
            `,
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            {/* Logo/Icon */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5, type: 'spring' }}
            >
              <Avatar
                sx={{
                  width: 64,
                  height: 64,
                  mx: 'auto',
                  mb: 2,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.3)}`,
                }}
              >
                {icon || <AccountBalanceWallet sx={{ fontSize: 32 }} />}
              </Avatar>
            </motion.div>

            {/* Title */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              <Typography
                variant="h4"
                component="h1"
                sx={{
                  fontWeight: 700,
                  mb: 1,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                {title}
              </Typography>
              
              {subtitle && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  {subtitle}
                </Typography>
              )}
            </motion.div>
          </Box>

          {/* Features */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-around',
              mb: 4,
              py: 2,
              borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            {[
              { icon: <Security />, label: 'Secure' },
              { icon: <TrendingUp />, label: 'Smart' },
              { icon: <AccountBalanceWallet />, label: 'Simple' }
            ].map((feature, index) => (
              <motion.div
                key={feature.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1, duration: 0.5 }}
                style={{ textAlign: 'center' }}
              >
                <Box
                  sx={{
                    color: 'text.secondary',
                    mb: 1,
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  {feature.icon}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {feature.label}
                </Typography>
              </motion.div>
            ))}
          </Box>

          {/* Form Content */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            {children}
          </motion.div>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default AuthCard;
