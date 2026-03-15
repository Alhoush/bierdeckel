import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../api';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [loyalty, setLoyalty] = useState([]);
    const [displayName, setDisplayName] = useState('');
    const [email, setEmail] = useState('');
    const [editing, setEditing] = useState(false);
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [changingPw, setChangingPw] = useState(false);
    const customerId = localStorage.getItem('customer_id');
    const restaurantId = localStorage.getItem('restaurant_id');
    const navigate = useNavigate();

    useEffect(() => {
        if (!customerId) return;
        loadProfile();
        loadLoyalty();
    }, []);

    const loadProfile = async () => {
        const res = await API.get(`/customer/${customerId}/profile`);
        setProfile(res.data);
        setDisplayName(res.data.display_name);
        setEmail(res.data.email || '');
    };

    const loadLoyalty = async () => {
        try {
            const res = await API.get(`/customer/${customerId}/loyalty/${restaurantId}`);
            setLoyalty(res.data);
        } catch (err) {}
    };

    const saveProfile = async () => {
        await API.put(`/customer/${customerId}/profile`, { display_name: displayName, email: email || null });
        localStorage.setItem('display_name', displayName);
        setEditing(false);
        loadProfile();
    };

    const uploadAvatar = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await API.put(`/customer/${customerId}/avatar`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            localStorage.setItem('avatar_url', res.data.avatar_url);
            loadProfile();
        } catch (err) {
            alert(err.response?.data?.detail || 'Upload fehlgeschlagen');
        }
    };

    const changePassword = async () => {
        try {
            await API.put(`/customer/${customerId}/password`, {
                old_password: oldPassword,
                new_password: newPassword
            });
            alert('Passwort geändert!');
            setChangingPw(false);
            setOldPassword('');
            setNewPassword('');
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const claimReward = async (programId) => {
        try {
            const res = await API.post(`/customer/${customerId}/loyalty/${programId}/claim`);
            alert(res.data.message);
            loadLoyalty();
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const deleteAccount = async () => {
        if (window.confirm('Konto wirklich löschen? Das kann nicht rückgängig gemacht werden!')) {
            await API.delete(`/customer/${customerId}`);
            localStorage.clear();
            navigate('/');
        }
    };

    const logout = () => {
        localStorage.removeItem('customer_id');
        localStorage.removeItem('display_name');
        localStorage.removeItem('avatar_url');
        navigate('/menu');
    };

    if (!customerId) {
        return (
            <div style={styles.container}>
                <h1 style={styles.title}>👤 Profil</h1>
                <div style={styles.card}>
                    <p style={styles.emptyText}>Du bist nicht eingeloggt.</p>
                    <p style={styles.emptyText}>Scanne den QR-Code und melde dich an!</p>
                </div>
                <div style={{ height: '100px' }}></div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>👤 Profil</h1>

            {profile && (
                <>
                    {/* Avatar */}
                    <div style={styles.avatarSection}>
                        {profile.avatar_url ? (
                            <img src={`http://127.0.0.1:8000${profile.avatar_url}`} alt="Avatar" style={styles.avatar} />
                        ) : (
                            <div style={styles.avatarPlaceholder}>👤</div>
                        )}
                        <label style={styles.uploadButton}>
                            📷 Bild ändern
                            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={uploadAvatar} style={{ display: 'none' }} />
                        </label>
                    </div>

                    {/* Info */}
                    <div style={styles.card}>
                        {!editing ? (
                            <>
                                <h2 style={styles.name}>{profile.display_name}</h2>
                                <p style={styles.info}>@{profile.username}</p>
                                <p style={styles.info}>{profile.email || 'Keine E-Mail'}</p>
                                <p style={styles.info}>Dabei seit: {new Date(profile.created_at).toLocaleDateString('de-DE')}</p>
                                <button onClick={() => setEditing(true)} style={styles.editButton}>✏️ Bearbeiten</button>
                            </>
                        ) : (
                            <>
                                <input placeholder="Anzeigename" value={displayName} onChange={e => setDisplayName(e.target.value)} style={styles.input} />
                                <input placeholder="E-Mail (optional)" value={email} onChange={e => setEmail(e.target.value)} style={styles.input} />
                                <button onClick={saveProfile} style={styles.saveButton}>💾 Speichern</button>
                                <button onClick={() => setEditing(false)} style={styles.cancelButton}>Abbrechen</button>
                            </>
                        )}
                    </div>

                    {/* Treuepunkte */}
                    {loyalty.length > 0 && (
                        <div style={styles.card}>
                            <h3 style={styles.sectionTitle}>🎁 Treuepunkte</h3>
                            {loyalty.map(l => (
                                <div key={l.program_id} style={styles.loyaltyItem}>
                                    <div>
                                        <p style={styles.loyaltyName}>{l.name}</p>
                                        <p style={styles.loyaltyInfo}>{l.menu_item} • {l.current_count}/{l.required_orders}</p>
                                        <div style={styles.progressBar}>
                                            <div style={{ ...styles.progressFill, width: `${Math.min(100, (l.current_count / l.required_orders) * 100)}%` }}></div>
                                        </div>
                                    </div>
                                    {l.reward_available && (
                                        <button onClick={() => claimReward(l.program_id)} style={styles.claimButton}>🎉 Einlösen!</button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Navigation */}
                    <div style={styles.card}>
                        <button onClick={() => navigate('/history')} style={styles.navButton}>📋 Bestellhistorie</button>
                        <button onClick={() => navigate('/leaderboard')} style={styles.navButton}>🏆 Rangliste</button>
                    </div>

                    {/* Passwort */}
                    <div style={styles.card}>
                        {!changingPw ? (
                            <button onClick={() => setChangingPw(true)} style={styles.editButton}>🔒 Passwort ändern</button>
                        ) : (
                            <>
                                <input placeholder="Altes Passwort" type="password" value={oldPassword} onChange={e => setOldPassword(e.target.value)} style={styles.input} />
                                <input placeholder="Neues Passwort" type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} style={styles.input} />
                                <button onClick={changePassword} style={styles.saveButton}>🔒 Ändern</button>
                                <button onClick={() => setChangingPw(false)} style={styles.cancelButton}>Abbrechen</button>
                            </>
                        )}
                    </div>

                    {/* Logout / Delete */}
                    <div style={styles.card}>
                        <button onClick={logout} style={styles.logoutButton}>🚪 Abmelden</button>
                        <button onClick={deleteAccount} style={styles.deleteButton}>🗑️ Konto löschen</button>
                    </div>
                </>
            )}

            <div style={{ height: '100px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    avatarSection: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '20px' },
    avatar: { width: '100px', height: '100px', borderRadius: '50%', objectFit: 'cover', border: '3px solid #e94560' },
    avatarPlaceholder: { width: '100px', height: '100px', borderRadius: '50%', background: '#1a1a2e', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px', border: '3px solid #333' },
    uploadButton: { marginTop: '10px', color: '#e94560', cursor: 'pointer', fontSize: '14px' },
    card: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', marginBottom: '15px', display: 'flex', flexDirection: 'column', gap: '10px' },
    name: { margin: 0, textAlign: 'center', fontSize: '22px' },
    info: { margin: 0, color: '#888', textAlign: 'center', fontSize: '14px' },
    input: { padding: '12px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px' },
    editButton: { padding: '10px', background: '#333', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    saveButton: { padding: '10px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    cancelButton: { padding: '10px', background: 'none', color: '#888', border: 'none', cursor: 'pointer', textAlign: 'center' },
    sectionTitle: { color: '#e94560', margin: '0 0 10px 0' },
    loyaltyItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #333' },
    loyaltyName: { margin: '0 0 3px 0', fontWeight: 'bold' },
    loyaltyInfo: { margin: '0 0 5px 0', color: '#888', fontSize: '12px' },
    progressBar: { width: '150px', height: '8px', background: '#333', borderRadius: '4px', overflow: 'hidden' },
    progressFill: { height: '100%', background: '#e94560', borderRadius: '4px', transition: 'width 0.3s' },
    claimButton: { padding: '8px 15px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', whiteSpace: 'nowrap' },
    navButton: { padding: '12px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', cursor: 'pointer', textAlign: 'center' },
    logoutButton: { padding: '10px', background: '#333', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    deleteButton: { padding: '10px', background: 'none', color: '#e94560', border: '1px solid #e94560', borderRadius: '8px', cursor: 'pointer' },
    emptyText: { color: '#888', textAlign: 'center', margin: '5px 0' }
};

export default Profile;