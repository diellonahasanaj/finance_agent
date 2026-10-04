import { useEffect, useState } from "react";
import API from "../../services/api";

function StatCard({ month }) {
	const [summary, setSummary] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchSummary();
		// eslint-disable-next-line
	}, [month]);

	const fetchSummary = async () => {
		setLoading(true);
		try {
			const response = await API.get("/analysis/monthly-summary", { params: { month } });
			setSummary(response.data);
		} catch (err) {
			setSummary(null);
		}
		setLoading(false);
	};

	if (loading) return <div>Loading...</div>;
	if (!summary) return <div>No data</div>;

	return (
		<div style={{ background: "#f3f4f6", padding: 20, borderRadius: 12, margin: 10 }}>
			<h4>Summary for {month}</h4>
			<div>Income: {summary.income}</div>
			<div>Expenses: {summary.expenses}</div>
			<div>Budget: {summary.budget}</div>
			<div>Debts: {summary.debts}</div>
		</div>
	);
}

export default StatCard;
