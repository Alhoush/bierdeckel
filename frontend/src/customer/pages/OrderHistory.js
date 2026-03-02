import React, { useEffect, useState } from 'react';
import API from '../../api';

function OrderHistory() {
    const [orders, setOrders] = useState([]);
    const sessionId = localStorage.getItem('session_id');

    useEffect(() => {
        async function loadOrders() {
            const res = await API.get(`/session/${sessionId}/orders`);
            setOrders(res.data);
        }
        loadOrders();
    }, [sessionId]);

    const statusLabels = {
        pending: '⏳ Bestellt',
        preparing: '👨‍🍳 In Zubereitung',
        delivered: '✅ Geliefert'
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>📋 Bestellungen</h1>

            {orders.length === 0 ? (
                <p style={styles.empty}>Noch keine Bestellungen</p>
            ) : (
                orders.map(order => (
                    <div key={order.order_id} style={styles.orderCard}>
                        <div style={styles.orderHeader}>
                            <span style={styles.status}>{statusLabels[order.status] || order.status}</span>
                            <span style={styles.total}>{order.total.toFixed(2)} €</span>
                        </div>
                        {order.items.map((item, i) => (
                            <p key={i} style={styles.item}>{item.quantity}x {item.name} - {item.price.toFixed(2)} €</p>
                        ))}
                        <p style={styles.time}>{order.created_at}</p>
                    </div>
                ))
            )}

            <div style={{ height: '80px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    empty: { textAlign: 'center', color: '#888', marginTop: '50px' },
    orderCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    orderHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' },
    status: { color: '#e94560', fontWeight: 'bold' },
    total: { color: '#e94560', fontWeight: 'bold' },
    item: { margin: '5px 0', color: '#ccc' },
    time: { color: '#666', fontSize: '12px', marginTop: '10px' }
};

export default OrderHistory;