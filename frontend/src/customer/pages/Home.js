import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../../api';

function Home() {
    const { restaurantId, bierdeckelId } = useParams();
    const navigate = useNavigate();
    const [view, setView] = useState('loading');
    const [sessionData, setSessionData] = useState(null);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        createSession();
    }, []);

    const createSession = async () => {
        try {
            const res = await API.post(`/r/${restaurantId}/bd/${bierdeckelId}/scan`);
            localStorage.setItem('session_id', res.data.session_id);
            localStorage.setItem('restaurant_id', res.data.restaurant_id);
            localStorage.setItem('bierdeckel_id', res.data.bierdeckel_id);
            localStorage.setItem('table_number', res.data.table_number);
            setSessionData(res.data);

            // Bereits eingeloggt?
            const customerId = localStorage.getItem('customer_id');
            if (customerId) {
                await API.put(`/session/${res.data.session_id}/link-customer/${customerId}`);
                navigate('/menu');
                return;
            }
            setView('welcome');
        } catch (err) {
            setView('error');
        }
    };

    const handleLogin = async () => {
        try {
            const res = await API.post('/customer/login', { username, password });
            localStorage.setItem('customer_id', res.data.customer_id);
            localStorage.setItem('display_name', res.data.display_name);
            localStorage.setItem('avatar_url', res.data.avatar_url || '');
            await API.put(`/session/${sessionData.session_id}/link-customer/${res.data.customer_id}`);
            navigate('/menu');
        } catch (err) {
            setError('Falsche Zugangsdaten');
        }
    };

    const handleRegister = async () => {
        if (!username || !password || !displayName) return setError('Alle Felder ausfüllen');
        try {
            const res = await API.post('/customer/register', { username, password, display_name: displayName });
            localStorage.setItem('customer_id', res.data.customer_id);
            localStorage.setItem('display_name', displayName);
            await API.put(`/session/${sessionData.session_id}/link-customer/${res.data.customer_id}`);
            navigate('/menu');
        } catch (err) {
            setError(err.response?.data?.detail || 'Fehler');
        }
    };

    const skipLogin = () => {
        navigate('/menu');
    };

    if (view === 'loading') return <div style={styles.container}><h2>⏳ Wird geladen...</h2></div>;
    if (view === 'error') return <div style={styles.container}><h2>❌ QR-Code ungültig</h2></div>;

    return (
        <div style={styles.container}>
            <h1 style={styles.logo}>🍺 Bierdeckel</h1>
            <p style={styles.tableInfo}>Tisch {sessionData?.table_number}</p>

            {view === 'welcome' && (
                <div style={styles.card}>
                    <h2 style={styles.cardTitle}>Willkommen!</h2>
                    <p style={styles.cardText}>Mit Konto: Treuepunkte, Rangliste & Profilbild</p>
                    <button onClick={() => setView('login')} style={styles.primaryButton}>🔑 Einloggen</button>
                    <button onClick={() => setView('register')} style={styles.secondaryButton}>📝 Registrieren</button>
                    <button onClick={skipLogin} style={styles.skipButton}>👤 Ohne Konto weiter</button>
                </div>
            )}

            {view === 'login' && (
                <div style={styles.card}>
                    <h2 style={styles.cardTitle}>Einloggen</h2>
                    {error && <p style={styles.error}>{error}</p>}
                    <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} style={styles.input} />
                    <input placeholder="Passwort" type="password" value={password} onChange={e => setPassword(e.target.value)} style={styles.input} />
                    <button onClick={handleLogin} style={styles.primaryButton}>Einloggen</button>
                    <button onClick={() => { setView('welcome'); setError(''); }} style={styles.skipButton}>← Zurück</button>
                </div>
            )}

            {view === 'register' && (
                <div style={styles.card}>
                    <h2 style={styles.cardTitle}>Registrieren</h2>
                    {error && <p style={styles.error}>{error}</p>}
                    <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} style={styles.input} />
                    <input placeholder="Anzeigename" value={displayName} onChange={e => setDisplayName(e.target.value)} style={styles.input} />
                    <input placeholder="Passwort" type="password" value={password} onChange={e => setPassword(e.target.value)} style={styles.input} />
                    <button onClick={handleRegister} style={styles.primaryButton}>Konto erstellen</button>
                    <button onClick={() => { setView('welcome'); setError(''); }} style={styles.skipButton}>← Zurück</button>
                </div>
            )}
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    logo: { color: '#e94560', fontSize: '36px', marginTop: '40px' },
    tableInfo: { color: '#888', fontSize: '16px', marginBottom: '30px' },
    card: { background: '#1a1a2e', padding: '30px', borderRadius: '15px', width: '100%', maxWidth: '350px', display: 'flex', flexDirection: 'column', gap: '12px' },
    cardTitle: { textAlign: 'center', margin: '0 0 5px 0' },
    cardText: { textAlign: 'center', color: '#888', fontSize: '13px', margin: 0 },
    input: { padding: '12px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '16px' },
    primaryButton: { padding: '14px', background: '#e94560', color: 'white', border: 'none', borderRadius: '10px', fontSize: '16px', cursor: 'pointer' },
    secondaryButton: { padding: '14px', background: '#1a1a2e', color: 'white', border: '1px solid #e94560', borderRadius: '10px', fontSize: '16px', cursor: 'pointer' },
    skipButton: { padding: '12px', background: 'none', color: '#888', border: 'none', fontSize: '14px', cursor: 'pointer' },
    error: { color: '#e94560', textAlign: 'center', margin: 0 }
};

export default Home;