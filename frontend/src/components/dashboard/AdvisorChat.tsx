import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Stack,
  Avatar,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Send as SendIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as UserIcon,
} from '@mui/icons-material';
// @ts-ignore
import API from '../../services/api';

interface ChatMessage {
  id: string;
  type: 'user' | 'advisor';
  content: string;
  timestamp: Date;
  data?: any;
}

interface AdvisorMessage {
  message: string;
  response: string;
  data?: any;
}

interface AdvisorChatProps {
  onClose?: () => void;
  compact?: boolean;
}

const AdvisorChat: React.FC<AdvisorChatProps> = ({ onClose, compact = false }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await API.post('/finance/ai-chat', { message: input });
      
      const advisorMessage: ChatMessage = {
        id: `advisor_${Date.now()}`,
        type: 'advisor',
        content: response.data.response,
        timestamp: new Date(),
        data: response.data.data,
      };

      setMessages((prev) => [...prev, advisorMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'advisor',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    inputRef.current?.focus();
  };

  const renderMessageContent = (msg: ChatMessage) => {
    if (msg.type === 'advisor' && msg.data) {
      return (
        <Box>
          <Typography variant="body2" sx={{ mb: 1, whiteSpace: 'pre-wrap' }}>
            {msg.content}
          </Typography>
          {msg.data.top_categories && msg.data.top_categories.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Stack direction="row" spacing={0.5} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                {msg.data.top_categories.map(([cat, amount]: [string, number], idx: number) => (
                  <Chip
                    key={idx}
                    label={`${cat}: $${amount.toFixed(2)}`}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Stack>
            </Box>
          )}
          {msg.data.balance !== undefined && (
            <Box sx={{ mt: 1 }}>
              <Chip
                label={`Balance: $${msg.data.balance.toFixed(2)}`}
                size="small"
                color={msg.data.balance >= 0 ? 'success' : 'error'}
                variant="filled"
              />
            </Box>
          )}
        </Box>
      );
    }
    return (
      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
        {msg.content}
      </Typography>
    );
  };

  const containerHeight = compact ? 'auto' : '600px';
  const messagesHeight = compact ? '300px' : '450px';

  return (
    <Paper
      elevation={3}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: containerHeight,
        borderRadius: 2,
        overflow: 'hidden',
        backgroundColor: theme.palette.background.paper,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <BotIcon />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Financial Advisor
          </Typography>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Clear chat">
            <IconButton
              size="small"
              onClick={handleClearChat}
              sx={{ color: 'white' }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          {onClose && (
            <Tooltip title="Close">
              <IconButton
                size="small"
                onClick={onClose}
                sx={{ color: 'white' }}
              >
                <CloseIcon />
              </IconButton>
            </Tooltip>
          )}
        </Stack>
      </Box>

      {/* Messages */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
          height: messagesHeight,
          backgroundColor: theme.palette.mode === 'dark'
            ? theme.palette.background.default
            : '#fafafa',
        }}
      >
        {messages.length === 0 && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: theme.palette.text.secondary,
            }}
          >
            <BotIcon sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />
            <Typography variant="body2" textAlign="center">
              Hello! I'm your Financial Advisor. Ask me about your spending, budget, or financial goals.
            </Typography>
          </Box>
        )}

        {messages.map((msg) => (
          <Box
            key={msg.id}
            sx={{
              display: 'flex',
              justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
              gap: 1,
            }}
          >
            {msg.type === 'advisor' && (
              <Avatar
                sx={{
                  backgroundColor: theme.palette.primary.main,
                  width: 32,
                  height: 32,
                  mt: 1,
                }}
              >
                <BotIcon sx={{ fontSize: 20 }} />
              </Avatar>
            )}

            <Card
              sx={{
                maxWidth: '70%',
                backgroundColor: msg.type === 'user'
                  ? theme.palette.primary.main
                  : theme.palette.mode === 'dark'
                  ? '#333'
                  : '#e3f2fd',
                color: msg.type === 'user' ? 'white' : 'inherit',
              }}
            >
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                {renderMessageContent(msg)}
                <Typography
                  variant="caption"
                  sx={{
                    mt: 1,
                    display: 'block',
                    opacity: 0.7,
                  }}
                >
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Typography>
              </CardContent>
            </Card>

            {msg.type === 'user' && (
              <Avatar
                sx={{
                  backgroundColor: theme.palette.success.main,
                  width: 32,
                  height: 32,
                  mt: 1,
                }}
              >
                <UserIcon sx={{ fontSize: 20 }} />
              </Avatar>
            )}
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Avatar
              sx={{
                backgroundColor: theme.palette.primary.main,
                width: 32,
                height: 32,
              }}
            >
              <BotIcon sx={{ fontSize: 20 }} />
            </Avatar>
            <CircularProgress size={24} sx={{ mt: 1 }} />
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box
        component="form"
        onSubmit={sendMessage}
        sx={{
          p: 2,
          borderTop: `1px solid ${theme.palette.divider}`,
          display: 'flex',
          gap: 1,
        }}
      >
        <TextField
          ref={inputRef}
          fullWidth
          placeholder="Ask about your finances..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          multiline
          maxRows={3}
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
            },
          }}
        />
        <Button
          type="submit"
          variant="contained"
          size="small"
          disabled={loading || !input.trim()}
          sx={{
            borderRadius: 2,
            minWidth: '50px',
          }}
        >
          {loading ? <CircularProgress size={20} /> : <SendIcon />}
        </Button>
      </Box>
    </Paper>
  );
};

export default AdvisorChat;
