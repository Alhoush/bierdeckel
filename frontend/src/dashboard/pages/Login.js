import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../api';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const res = await API.post('/auth/login', { username, password });
            localStorage.setItem('token', res.data.token);
            localStorage.setItem('username', res.data.username);
            localStorage.setItem('role', res.data.role);
            localStorage.setItem('restaurant_id', res.data.restaurant_id);
            navigate('/dashboard');
        } catch (err) {
            setError('Falsche Zugangsdaten');
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.loginBox}>
                <h1 style={styles.title}>🍺 Bierdeckel</h1>
                <h2 style={styles.subtitle}>Service Login</h2>

                {error && <p style={styles.error}>{error}</p>}

                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={styles.input}
                />
                <input
                    type="password"
                    placeholder="Passwort"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={styles.input}
                />
                <button onClick={handleLogin} style={styles.button}>
                    Einloggen
                </button>
            </div>
        </div>
    );
}

const styles = {
    container: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#0f0f23' },
    loginBox: { background: '#1a1a2e', padding: '40px', borderRadius: '15px', width: '350px', textAlign: 'center' },
    title: { color: '#e94560', margin: '0 0 5px 0' },
    subtitle: { color: '#888', margin: '0 0 25px 0', fontWeight: 'normal' },
    input: { width: '100%', padding: '12px', marginBottom: '15px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' },
    button: { width: '100%', padding: '12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer' },
    error: { color: '#e94560', marginBottom: '15px' }
};

export default Login;