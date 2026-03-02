import DashboardNav from '../components/DashboardNav';
import React, { useState } from 'react';
import API from '../../api';

function StaffManager() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('staff');
    const [message, setMessage] = useState('');
    const restaurantId = localStorage.getItem('restaurant_id');

    const addStaff = async () => {
        if (!username || !password) return alert('Alle Felder ausfüllen');
        try {
            await API.post(`/auth/register-staff/${restaurantId}`, {
                username, password, role
            });
            setMessage(`✅ ${username} als ${role} erstellt!`);
            setUsername('');
            setPassword('');
        } catch (err) {
            setMessage(`❌ ${err.response?.data?.detail || 'Fehler'}`);
        }
    };

    return (
        <>

            <DashboardNav />
            <div style={styles.container}>
                <h1 style={styles.title}>👥 Mitarbeiter verwalten</h1>

                <div style={styles.addForm}>
                    <h3 style={styles.formTitle}>Neuer Mitarbeiter</h3>

                    <input
                        placeholder="Username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        style={styles.input}
                    />
                    <input
                        placeholder="Passwort"
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        style={styles.input}
                    />

                    <div style={styles.roleRow}>
                        <button
                            onClick={() => setRole('staff')}
                            style={role === 'staff' ? styles.roleActive : styles.roleButton}
                        >
                            🧑‍🍳 Kellner
                        </button>
                        <button
                            onClick={() => setRole('admin')}
                            style={role === 'admin' ? styles.roleActive : styles.roleButton}
                        >
                            👑 Admin
                        </button>
                    </div>

                    <button onClick={addStaff} style={styles.addButton}>
                        + Mitarbeiter anlegen
                    </button>

                    {message && <p style={styles.message}>{message}</p>}
                </div>
            </div>
        </>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    addForm: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', maxWidth: '400px', margin: '0 auto' },
    formTitle: { margin: '0 0 15px 0', color: '#e94560' },
    input: { width: '100%', padding: '12px', marginBottom: '15px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' },
    roleRow: { display: 'flex', gap: '10px', marginBottom: '15px' },
    roleButton: { flex: 1, padding: '12px', background: '#333', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    roleActive: { flex: 1, padding: '12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    addButton: { width: '100%', padding: '12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer' },
    message: { textAlign: 'center', marginTop: '15px' }
};

export default StaffManager;