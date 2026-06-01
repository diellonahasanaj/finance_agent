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
			// Replace with actual GET endpoint for expenses if available
			const response = await API.get("/expenses");
			setExpenses(response.data);
		} catch (err) {
			setExpenses([]);
		}
		setLoading(false);
	};

	if (loading) return <div>Loading...</div>;

	return (
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Category</th>
					<th>Description</th>
					<th>Amount</th>
				</tr>
			</thead>
			<tbody>
				{expenses.map((exp, idx) => (
					<tr key={idx}>
						<td>{exp.date}</td>
						<td>{exp.category}</td>
						<td>{exp.description}</td>
						<td>{exp.amount}</td>
					</tr>
				))}
			</tbody>
		</table>
	);
}

export default ExpenseTable;
