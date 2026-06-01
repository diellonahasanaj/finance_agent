import { Drawer, List, ListItem, ListItemText, Toolbar } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';

const drawerWidth = 220;

const navItems = [
	{ text: 'Dashboard', link: '/' },
	{ text: 'Add Expense', link: '/add-expense' },
	{ text: 'Set Budget', link: '/set-budget' },
	{ text: 'Reports', link: '/reports' },
];

function SideBar() {
	const navigate = useNavigate();

	const handleLogout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		navigate('/login');
	};

	return (
		<Drawer
			variant="permanent"
			sx={{
				width: drawerWidth,
				flexShrink: 0,
				[`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', background: '#1a1a2e', color: '#fff' },
			}}
		>
			<Toolbar />
			<List>
				{navItems.map(({ text, link }) => (
					<ListItem key={text} component={Link} to={link} sx={{ color: '#fff', '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' } }}>
						<ListItemText primary={text} />
					</ListItem>
				))}
				<ListItem onClick={handleLogout} sx={{ color: '#fff', cursor: 'pointer', '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' } }}>
					<ListItemText primary="Logout" />
				</ListItem>
			</List>
		</Drawer>
	);
}

export default SideBar;
