import React, { useEffect, useState } from 'react';
import API from '../../api';

function History() {
    const [history, setHistory] = useState([]);
    const customerId = localStorage.getItem('customer_id');

    useEffect(() => {
        if (customerId) loadHistory();
    }, []);

    const loadHistory = async () => {
        const res = await API.get(`/customer/${customerId}/history`);
        setHistory(res.data);
    };

    if (!customerId) {
        return (
            <div style={styles.container}>
                <h1 style={styles.title}>📋 Bestellhistorie</h1>
                <p style={styles.empty}>Melde dich an um deine Bestellhistorie zu sehen.</p>
                <div style={{ height: '100px' }}></div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>📋 Bestellhistorie</h1>

            {history.length === 0 ? (
                <p style={styles.empty}>Noch keine Bestellungen</p>
            ) : (
                history.map(visit => (
                    <div key={visit.session_id} style={styles.visitCard}>
                        <div style={styles.visitHeader}>
                            <span>📅 {new Date(visit.date).toLocaleDateString('de-DE')}</span>
                            <span style={styles.tableBadge}>Tisch {visit.table_number}</span>
                        </div>
                        {visit.items.map((item, i) => (
                            <div key={i} style={styles.itemRow}>
                                <span>{item.quantity}x {item.name}</span>
                                <span>{item.subtotal.toFixed(2)} €</span>
                            </div>
                        ))}
                        <div style={styles.totalRow}>
                            <span>Gesamt:</span>
                            <span>{visit.total.toFixed(2)} €</span>
                        </div>
                        <div style={styles.statusRow}>
                            {visit.paid >= visit.total ? (
                                <span style={styles.paid}>✅ Bezahlt</span>
                            ) : visit.is_active ? (
                                <span style={styles.active}>🟢 Aktiv</span>
                            ) : (
                                <span style={styles.unpaid}>⚠️ Offen: {(visit.total - visit.paid).toFixed(2)} €</span>
                            )}
                        </div>
                    </div>
                ))
            )}

            <div style={{ height: '100px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' },
    visitCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '15px' },
    visitHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px', fontSize: '14px', color: '#ccc' },
    tableBadge: { background: '#333', padding: '2px 10px', borderRadius: '10px', fontSize: '12px' },
    itemRow: { display: 'flex', justifyContent: 'space-between', padding: '5px 0', color: '#ccc', fontSize: '14px', borderBottom: '1px solid #222' },
    totalRow: { display: 'flex', justifyContent: 'space-between', paddingTop: '10px', fontWeight: 'bold', color: '#e94560' },
    statusRow: { marginTop: '8px', textAlign: 'right' },
    paid: { color: '#4CAF50', fontSize: '13px' },
    active: { color: '#4CAF50', fontSize: '13px' },
    unpaid: { color: '#ff9800', fontSize: '13px' }
};

export default History;