import React, { useEffect, useState } from 'react';
import API from '../../api';

function DrinkTogether() {
    const [readyList, setReadyList] = useState([]);
    const [isReady, setIsReady] = useState(false);
    const [invitations, setInvitations] = useState([]);
    const [group, setGroup] = useState(null);
    const sessionId = localStorage.getItem('session_id');
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        const readyRes = await API.get(`/restaurant/${restaurantId}/drink-ready`);
        setReadyList(readyRes.data);

        const invRes = await API.get(`/session/${sessionId}/invitations`);
        setInvitations(invRes.data);

        // Prüfen ob in Gruppe
        try {
            const sessionRes = await API.get(`/session/${sessionId}`);
            if (sessionRes.data.group_id) {
                const groupRes = await API.get(`/group/${sessionRes.data.group_id}`);
                setGroup(groupRes.data);
            }
        } catch (err) {}
    };

    const toggleReady = async () => {
        await API.put(`/session/${sessionId}/drink-ready`);
        setIsReady(!isReady);
        loadData();
    };

    const sendInvite = async (targetSessionId) => {
        try {
            const res = await API.post(`/session/${sessionId}/invite/${targetSessionId}`);
            alert(`Einladung gesendet!`);
            loadData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const acceptInvite = async (invitationId, groupId) => {
        await API.put(`/invitation/${invitationId}/accept`);
        setIsReady(false);
        const groupRes = await API.get(`/group/${groupId}`);
        setGroup(groupRes.data);
        setInvitations([]);
        loadData();
    };

    const declineInvite = async (invitationId) => {
        await API.put(`/invitation/${invitationId}/decline`);
        loadData();
    };

    const leaveGroup = async () => {
        await API.put(`/session/${sessionId}/leave-group`);
        setGroup(null);
        loadData();
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>🍻 Zusammen trinken</h1>

            {/* Gruppe anzeigen */}
            {group && (
                <div style={styles.section}>
                    <div style={styles.groupCard}>
                        <h2 style={styles.groupTitle}>👥 Deine Gruppe</h2>
                        <p style={styles.groupCode}>Code: <strong>{group.invite_code}</strong></p>
                        <p style={styles.groupId}>Gruppe-ID: {group.group_id}</p>

                        <div style={styles.memberList}>
                            {group.members.map(m => (
                                <div key={m.session_id} style={styles.memberCard}>
                                    <span>🪑 Tisch {m.table_number}</span>
                                    {m.session_id === sessionId && <span style={styles.youBadge}>Du</span>}
                                </div>
                            ))}
                        </div>

                        <button onClick={leaveGroup} style={styles.leaveButton}>
                            🚪 Gruppe verlassen
                        </button>
                    </div>
                </div>
            )}

            {/* Einladungen */}
            {invitations.length > 0 && (
                <div style={styles.section}>
                    <h2 style={styles.subtitle}>📩 Einladungen</h2>
                    {invitations.map(inv => (
                        <div key={inv.invitation_id} style={styles.inviteCard}>
                            <p style={styles.inviteText}>Tisch {inv.from_table} möchte mit dir trinken!</p>
                            <div style={styles.buttonRow}>
                                <button onClick={() => acceptInvite(inv.invitation_id, inv.group_id)} style={styles.acceptButton}>
                                    ✅ Annehmen
                                </button>
                                <button onClick={() => declineInvite(inv.invitation_id)} style={styles.declineButton}>
                                    ❌ Ablehnen
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Bereit-Button (nur wenn nicht in Gruppe) */}
            {!group && (
                <button onClick={toggleReady} style={isReady ? styles.readyActive : styles.readyButton}>
                    {isReady ? '✅ Du bist bereit!' : '🍺 Bereit zum Trinken?'}
                </button>
            )}

            {/* Bereit-Liste (nur wenn nicht in Gruppe) */}
            {!group && (
                <div style={styles.section}>
                    <h2 style={styles.subtitle}>🔍 Wer ist bereit?</h2>
                    {readyList.filter(r => r.session_id !== sessionId).length === 0 ? (
                        <p style={styles.empty}>Noch niemand bereit</p>
                    ) : (
                        readyList.filter(r => r.session_id !== sessionId).map(r => (
                            <div key={r.session_id} style={styles.readyCard}>
                                <span>🪑 Tisch {r.table_number}</span>
                                <button onClick={() => sendInvite(r.session_id)} style={styles.inviteButton}>
                                    Einladen
                                </button>
                            </div>
                        ))
                    )}
                </div>
            )}

            <div style={{ height: '100px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    section: { marginTop: '20px' },
    subtitle: { color: '#e94560', fontSize: '18px' },
    groupCard: { background: '#1a1a2e', padding: '20px', borderRadius: '12px', border: '1px solid #e94560' },
    groupTitle: { color: '#e94560', margin: '0 0 10px 0' },
    groupCode: { fontSize: '18px', marginBottom: '5px' },
    groupId: { color: '#666', fontSize: '12px', marginBottom: '15px' },
    memberList: { marginBottom: '15px' },
    memberCard: { display: 'flex', justifyContent: 'space-between', background: '#0f0f23', padding: '10px 15px', borderRadius: '8px', marginBottom: '5px' },
    youBadge: { background: '#e94560', color: 'white', padding: '2px 10px', borderRadius: '10px', fontSize: '12px' },
    leaveButton: { width: '100%', padding: '12px', background: '#333', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    inviteCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    inviteText: { marginBottom: '10px' },
    buttonRow: { display: 'flex', gap: '10px' },
    acceptButton: { flex: 1, padding: '10px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    declineButton: { flex: 1, padding: '10px', background: '#666', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    readyButton: { width: '100%', padding: '15px', background: '#1a1a2e', color: 'white', border: '1px solid #e94560', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', marginTop: '15px' },
    readyActive: { width: '100%', padding: '15px', background: '#e94560', color: 'white', border: 'none', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', marginTop: '15px' },
    readyCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1a1a2e', padding: '12px 15px', borderRadius: '8px', marginBottom: '8px' },
    inviteButton: { background: '#e94560', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' },
    empty: { color: '#888' }
};

export default DrinkTogether;