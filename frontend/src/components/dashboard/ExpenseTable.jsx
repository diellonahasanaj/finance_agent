import { useEffect, useState } from "react";
import API from "../../services/api";

function ExpenseTable() {
	const [expenses, setExpenses] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchExpenses();
	}, []);

	const fetchExpenses = async () => {
		setLoading(true);
		try {
			// Use correct API endpoint for expenses
			const response = await API.get("/finance/expense");
			setExpenses(response.data || []);
		} catch (err) {
			console.error("Failed to fetch expenses:", err);
			setExpenses([]);
		}
		setLoading(false);
	};

	if (loading) return <div>Loading...</div>;

	if (expenses.length === 0) {
		return <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>No expenses recorded yet</div>;
	}

	return (
		<table style={{ width: '100%', borderCollapse: 'collapse' }}>
			<thead>
				<tr style={{ backgroundColor: '#f5f5f5' }}>
					<th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Date</th>
					<th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Category</th>
					<th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Description</th>
					<th style={{ padding: '10px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>Amount</th>
				</tr>
			</thead>
			<tbody>
				{expenses.map((exp, idx) => (
					<tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
						<td style={{ padding: '10px' }}>{exp.date}</td>
						<td style={{ padding: '10px' }}>{exp.category}</td>
						<td style={{ padding: '10px' }}>{exp.description || '-'}</td>
						<td style={{ padding: '10px', textAlign: 'right' }}>${parseFloat(exp.amount).toFixed(2)}</td>
					</tr>
				))}
			</tbody>
		</table>
	);
}

export default ExpenseTable;

