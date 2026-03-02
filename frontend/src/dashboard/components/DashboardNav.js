import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function DashboardNav() {
    const navigate = useNavigate();
    const location = useLocation();
    const role = localStorage.getItem('role');
    const username = localStorage.getItem('username');

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        navigate('/login');
    };

    const links = [
        { path: '/dashboard', label: '📊 Dashboard' },
        { path: '/dashboard/tables', label: '🪑 Tische', adminOnly: true },
        { path: '/dashboard/menu', label: '📋 Menü', adminOnly: true },
        { path: '/dashboard/staff', label: '👥 Personal', adminOnly: true },
    ];

    return (
        <div style={styles.nav}>
            <h2 style={styles.logo}>🍺 Bierdeckel</h2>
            <div style={styles.links}>
                {links
                    .filter(link => !link.adminOnly || role === 'owner' || role === 'admin')
                    .map(link => (
                        <button
                            key={link.path}
                            onClick={() => navigate(link.path)}
                            style={location.pathname === link.path ? styles.activeLink : styles.link}
                        >
                            {link.label}
                        </button>
                    ))}
            </div>
            <div style={styles.rightSection}>
                <span style={styles.userInfo}>👤 {username} ({role})</span>
                <button onClick={logout} style={styles.logoutButton}>🚪 Abmelden</button>
            </div>
        </div>
    );
}

const styles = {
    nav: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#1a1a2e', padding: '10px 20px', borderBottom: '1px solid #333' },
    logo: { color: '#e94560', margin: 0, fontSize: '18px' },
    links: { display: 'flex', gap: '5px' },
    link: { background: 'none', color: '#888', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    activeLink: { background: '#e94560', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    rightSection: { display: 'flex', alignItems: 'center', gap: '15px' },
    userInfo: { color: '#888', fontSize: '14px' },
    logoutButton: { background: '#333', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' }
};

export default DashboardNav;