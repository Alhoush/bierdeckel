import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import API from '../../api';

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const interval = setInterval(checkSession, 5000);
        return () => clearInterval(interval);
    }, []);

    const checkSession = async () => {
        const sessionId = localStorage.getItem('session_id');
        if (!sessionId) return;
        try {
            const res = await API.get(`/session/${sessionId}`);
            if (!res.data.is_active) {
                alert('Deine Session wurde vom Service beendet. Tschüss!');
                localStorage.clear();
                navigate('/');
            }
        } catch (err) {
            localStorage.clear();
            navigate('/');
        }
    };

    const tabs = [
        { path: '/menu', label: '🍺', name: 'Menü' },
        { path: '/cart', label: '🛒', name: 'Warenkorb' },
        { path: '/orders', label: '📋', name: 'Bestellungen' },
        { path: '/payment', label: '💳', name: 'Bezahlen' },
        { path: '/drink', label: '🍻', name: 'Zusammen' },
        { path: '/game', label: '🎮', name: 'Spiel' },
        { path: '/leaderboard', label: '🏆', name: 'Rang' },
        { path: '/profile', label: '👤', name: 'Profil' },
    ];

    return (
        <div style={styles.navbar}>
            {tabs.map(tab => (
                <button
                    key={tab.path}
                    onClick={() => navigate(tab.path)}
                    style={location.pathname === tab.path ? styles.activeTab : styles.tab}
                >
                    <span style={styles.icon}>{tab.label}</span>
                    <span style={styles.tabName}>{tab.name}</span>
                </button>
            ))}
        </div>
    );
}

const styles = {
    navbar: { position: 'fixed', bottom: 0, left: 0, right: 0, display: 'flex', background: '#1a1a2e', borderTop: '1px solid #333', padding: '5px 0', zIndex: 999 },
    tab: { flex: 1, background: 'none', color: '#888', border: 'none', padding: '8px 0', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    activeTab: { flex: 1, background: 'none', color: '#e94560', border: 'none', padding: '8px 0', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    icon: { fontSize: '18px' },
    tabName: { fontSize: '10px', marginTop: '2px' }
};

export default Navbar;