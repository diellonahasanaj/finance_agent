import { useEffect, useState } from "react";
import API from "../../services/api";
import { Lightbulb as LightbulbIcon } from '@mui/icons-material';
import { Card, CardContent, Typography, Box, CircularProgress, Alert, Stack } from '@mui/material';

function AdvisorPanel() {
  const [advice, setAdvice] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    fetchAdvice();
  }, []);

  const fetchAdvice = async () => {
    setLoading(true);
    setError("");
    try {
      // Get financial recommendations from the planning endpoint
      const response = await API.get("/planning/recommendations");
      
      if (response.data && response.data.recommendations) {
        setRecommendations(response.data.recommendations.slice(0, 3)); // Show top 3
        
        if (response.data.recommendations.length > 0) {
          const topRec = response.data.recommendations[0];
          setAdvice(topRec.description || topRec.title);
        } else {
          setAdvice("Keep tracking your expenses to receive personalized recommendations.");
        }
      } else {
        setAdvice("Add financial data to receive personalized recommendations.");
      }
    } catch (error) {
      console.error("Error fetching advice:", error);
      setError("Unable to load recommendations at this time.");
      setAdvice("Check back later for financial insights.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card sx={{ mt: 2 }}>
        <CardContent sx={{ display: 'flex', justifyContent: 'center', minHeight: 120 }}>
          <CircularProgress size={30} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mt: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <LightbulbIcon sx={{ color: '#fff', fontSize: 28 }} />
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
            AI Financial Advisor
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="warning" sx={{ mb: 1 }}>
            {error}
          </Alert>
        )}

        <Typography variant="body2" sx={{ color: '#fff', mb: 2, opacity: 0.95 }}>
          {advice}
        </Typography>

        {recommendations.length > 0 && (
          <Stack spacing={1} sx={{ mt: 2 }}>
            <Typography variant="caption" sx={{ color: '#fff', opacity: 0.8 }}>
              Other Recommendations:
            </Typography>
            {recommendations.slice(1).map((rec, idx) => (
              <Typography
                key={idx}
                variant="body2"
                sx={{
                  color: '#fff',
                  opacity: 0.9,
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                }}
              >
                <span style={{ marginRight: 8 }}>•</span>
                {rec.title}
              </Typography>
            ))}
          </Stack>
        )}

        <Typography variant="caption" sx={{ mt: 2, display: 'block', color: '#fff', opacity: 0.7 }}>
          Visit the Financial Advisor page for personalized guidance.
        </Typography>
      </CardContent>
    </Card>
  );
}

export default AdvisorPanel;

