import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../api';

function Payment() {
    const [bill, setBill] = useState(null);
    const [groupBill, setGroupBill] = useState(null);
    const [paid, setPaid] = useState(false);
    const [showGroup, setShowGroup] = useState(false);
    const sessionId = localStorage.getItem('session_id');
    const navigate = useNavigate();

    useEffect(() => {
        loadBill();
        loadGroupBill();
    }, []);

    const loadBill = async () => {
        try {
            const res = await API.get(`/session/${sessionId}/bill`);
            setBill(res.data);
        } catch (err) {}
    };

    const loadGroupBill = async () => {
        try {
            const res = await API.get(`/session/${sessionId}/group-bill`);
            setGroupBill(res.data);
        } catch (err) {
            setGroupBill(null);
        }
    };

    const requestPayment = async () => {
        await API.post(`/session/${sessionId}/payment-request`);
        alert('Zahlungswunsch an Kellner gesendet!');
    };

    const payNow = async () => {
        await API.post(`/session/${sessionId}/pay`);
        setPaid(true);
        loadBill();
    };

    const payForGroup = async () => {
        if (window.confirm('Für alle in der Gruppe bezahlen?')) {
            const res = await API.post(`/session/${sessionId}/pay-group`);
            alert(res.data.message);
            setPaid(true);
            loadBill();
            loadGroupBill();
        }
    };

    const closeAndLeave = async () => {
        await API.put(`/session/${sessionId}/close`);
        localStorage.clear();
        navigate('/');
    };

    if (paid) {
        return (
            <div style={styles.container}>
                <div style={styles.success}>
                    <h2>✅ Bezahlt!</h2>
                    <p>Vielen Dank für deinen Besuch!</p>
                    <button onClick={closeAndLeave} style={styles.leaveButton}>
                        👋 Tisch verlassen
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>💳 Bezahlen</h1>

            {/* Tab-Auswahl wenn Gruppe existiert */}
            {groupBill && (
                <div style={styles.tabRow}>
                    <button
                        onClick={() => setShowGroup(false)}
                        style={!showGroup ? styles.activeTab : styles.tab}
                    >
                        Meine Rechnung
                    </button>
                    <button
                        onClick={() => setShowGroup(true)}
                        style={showGroup ? styles.activeTab : styles.tab}
                    >
                        Gruppen-Rechnung
                    </button>
                </div>
            )}

            {/* Meine Rechnung */}
            {!showGroup && bill && (
                <>
                    <div style={styles.billCard}>
                        <h3 style={styles.billTitle}>📋 Deine Bestellungen</h3>
                        {bill.items.map((item, i) => (
                            <div key={i} style={styles.billItem}>
                                <div>
                                    <span>{item.quantity}x {item.name}</span>
                                    {item.source_label && (
                                        <span style={item.source === 'game_loser' ? styles.gameLoser : styles.gameWinner}>
                                            {' '}{item.source_label}
                                        </span>
                                    )}
                                </div>
                                <span>{item.subtotal.toFixed(2)} €</span>
                            </div>
                        ))}
                        <div style={styles.billDivider}></div>
                        <div style={styles.billRow}>
                            <span>Gesamt:</span>
                            <span>{bill.total.toFixed(2)} €</span>
                        </div>
                        <div style={styles.billRow}>
                            <span>Bereits bezahlt:</span>
                            <span>{bill.already_paid.toFixed(2)} €</span>
                        </div>
                        <div style={styles.billTotal}>
                            <span>Noch offen:</span>
                            <span>{bill.remaining.toFixed(2)} €</span>
                        </div>
                    </div>

                    <button onClick={requestPayment} style={styles.requestButton}>
                        🔔 Kellner zum Bezahlen rufen
                    </button>
                    <button onClick={payNow} style={styles.payButton}>
                        💳 Jetzt bezahlen
                    </button>
                </>
            )}

            {/* Gruppen-Rechnung */}
            {showGroup && groupBill && (
                <>
                    <div style={styles.billCard}>
                        <h3 style={styles.billTitle}>👥 Gruppen-Bestellungen</h3>
                        {groupBill.items.map((item, i) => (
                            <div key={i} style={styles.billItem}>
                                <span>
                                    <span style={styles.tableBadge}>T{item.table_number}</span>
                                    {item.quantity}x {item.name}
                                </span>
                                <span>{item.subtotal.toFixed(2)} €</span>
                            </div>
                        ))}
                        <div style={styles.billDivider}></div>
                        <div style={styles.billRow}>
                            <span>Gruppen-Gesamt:</span>
                            <span>{groupBill.group_total.toFixed(2)} €</span>
                        </div>
                        <div style={styles.billRow}>
                            <span>Bereits bezahlt:</span>
                            <span>{groupBill.group_paid.toFixed(2)} €</span>
                        </div>
                        <div style={styles.billTotal}>
                            <span>Noch offen:</span>
                            <span>{groupBill.group_remaining.toFixed(2)} €</span>
                        </div>
                    </div>

                    <button onClick={payForGroup} style={styles.payGroupButton}>
                        💳 Für alle bezahlen ({groupBill.group_remaining.toFixed(2)} €)
                    </button>
                </>
            )}

            <div style={{ height: '100px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    tabRow: { display: 'flex', gap: '10px', marginBottom: '20px' },
    tab: { flex: 1, padding: '12px', background: '#1a1a2e', color: '#888', border: '1px solid #333', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    activeTab: { flex: 1, padding: '12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px' },
    billCard: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', marginBottom: '20px' },
    billTitle: { color: '#e94560', margin: '0 0 15px 0' },
    billItem: { display: 'flex', justifyContent: 'space-between', padding: '8px 0', color: '#ccc', borderBottom: '1px solid #222' },
    billDivider: { borderTop: '2px solid #333', margin: '10px 0' },
    billRow: { display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#ccc' },
    billTotal: { display: 'flex', justifyContent: 'space-between', paddingTop: '10px', borderTop: '1px solid #333', color: '#e94560', fontWeight: 'bold', fontSize: '20px' },
    tableBadge: { background: '#333', color: '#888', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', marginRight: '8px' },
    requestButton: { width: '100%', padding: '15px', background: '#1a1a2e', color: 'white', border: '1px solid #e94560', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', marginBottom: '10px' },
    payButton: { width: '100%', padding: '15px', background: '#e94560', color: 'white', border: 'none', borderRadius: '10px', fontSize: '18px', cursor: 'pointer' },
    payGroupButton: { width: '100%', padding: '15px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '10px', fontSize: '18px', cursor: 'pointer' },
    success: { textAlign: 'center', marginTop: '100px' },
    leaveButton: { marginTop: '20px', padding: '15px 40px', background: '#333', color: 'white', border: 'none', borderRadius: '10px', fontSize: '16px', cursor: 'pointer' },
    gameLoser: { fontSize: '11px', color: '#e94560', display: 'block' },
    gameWinner: { fontSize: '11px', color: '#4CAF50', display: 'block' },
};

export default Payment;