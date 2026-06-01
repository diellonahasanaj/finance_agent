import { useEffect, useState } from "react";
import API from "../../services/api";

function AdvisorPanel() {
  const [advice, setAdvice] = useState("");

  useEffect(() => {
    fetchAdvice();
  }, []);

  const fetchAdvice = async () => {
    try {
      const response = await API.get("/advisor");
      setAdvice(response.data.message);
    } catch (error) {
      console.error("Error fetching advice:", error);
    }
  };

  return (
    <div style={styles.card}>
      <h3>AI Financial Advisor</h3>
      <p>{advice}</p>
    </div>
  );
}

const styles = {
  card: {
    background: "#f3f4f6",
    padding: "20px",
    borderRadius: "12px",
    marginTop: "20px"
  }
};

export default AdvisorPanel;
