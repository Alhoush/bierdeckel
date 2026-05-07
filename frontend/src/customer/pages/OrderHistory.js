import React, { useEffect, useState } from 'react';
import API from '../../api';

function OrderHistory() {
    const [orders, setOrders] = useState([]);
    const [autoOrder, setAutoOrder] = useState(null);
    const [menuItems, setMenuItems] = useState([]);
    const [selectedItem, setSelectedItem] = useState('');
    const sessionId = localStorage.getItem('session_id');
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadOrders();
        loadAutoOrder();
        loadMenu();
        const interval = setInterval(loadOrders, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadOrders = async () => {
        try {
            const res = await API.get(`/session/${sessionId}/orders`);
            setOrders(res.data);
        } catch (err) {}
    };

    const loadAutoOrder = async () => {
        try {
            const res = await API.get(`/session/${sessionId}/auto-order`);
            setAutoOrder(res.data);
        } catch (err) {}
    };

    const loadMenu = async () => {
        try {
            const res = await API.get(`/restaurant/${restaurantId}/menu`);
            const allItems = Object.values(res.data).flat();
            setMenuItems(allItems);
        } catch (err) {}
    };

    const toggleAutoOrder = async () => {
        if (autoOrder && autoOrder.auto_order) {
            // Ausschalten
            await API.put(`/session/${sessionId}/auto-order`, { enabled: false });
        } else {
            // Einschalten
            await API.put(`/session/${sessionId}/auto-order`, {
                enabled: true,
                menu_item_id: selectedItem || null
            });
        }
        loadAutoOrder();
    };

    const statusLabel = {
        pending: '⏳ Bestellt',
        preparing: '👨‍🍳 Zubereitung',
        delivered: '✅ Geliefert'
    };

    const sourceLabel = {
        manual: null,
        auto_order: '🔄 Auto-Bestellung',
        game_loser: '🎮 Spiel (du zahlst)',
        game_winner: '🎮 Spiel (gratis!)'
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>📋 Bestellungen</h1>

            {/* Auto-Bestellung */}
            <div style={styles.autoCard}>
                <div style={styles.autoHeader}>
                    <h3 style={styles.autoTitle}>🔄 Auto-Nachbestellung</h3>
                    <button
                        onClick={toggleAutoOrder}
                        style={autoOrder?.auto_order ? styles.autoOnButton : styles.autoOffButton}
                    >
                        {autoOrder?.auto_order ? 'AN' : 'AUS'}
                    </button>
                </div>

                {autoOrder?.auto_order ? (
                    <p style={styles.autoInfo}>
                        Nachbestellen: <strong>{autoOrder.item_name}</strong><br />
                        Wenn dein Glas leer ist, wird automatisch nachbestellt!
                    </p>
                ) : (
                    <div>
                        <p style={styles.autoInfo}>Wähle ein Getränk für Auto-Nachbestellung:</p>
                        <select
                            value={selectedItem}
                            onChange={e => setSelectedItem(e.target.value)}
                            style={styles.select}
                        >
                            <option value="">Letztes Getränk verwenden</option>
                            {menuItems.map(item => (
                                <option key={item.id} value={item.id}>
                                    {item.name} - {item.price.toFixed(2)} €
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {/* Bestellungen */}
            {orders.length === 0 ? (
                <p style={styles.empty}>Noch keine Bestellungen</p>
            ) : (
                orders.map(order => (
                    <div key={order.order_id} style={styles.orderCard}>
                        <div style={styles.orderHeader}>
                            <span style={styles.status}>{statusLabel[order.status] || order.status}</span>
                            <span style={styles.orderTime}>
                                {new Date(order.created_at).toLocaleTimeString('de-DE')}
                            </span>
                        </div>
                        {order.items.map((item, i) => (
                            <div key={i} style={styles.itemRow}>
                                <span>{item.quantity}x {item.name}</span>
                                <span>{(item.price * item.quantity).toFixed(2)} €</span>
                            </div>
                        ))}
                        {sourceLabel[order.source] && (
                            <p style={styles.sourceTag}>{sourceLabel[order.source]}</p>
                        )}
                        <div style={styles.totalRow}>
                            <span>Gesamt:</span>
                            <span>{order.total.toFixed(2)} €</span>
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
    autoCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #333' },
    autoHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    autoTitle: { margin: 0, fontSize: '16px' },
    autoOnButton: { padding: '8px 20px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold' },
    autoOffButton: { padding: '8px 20px', background: '#333', color: '#888', border: '1px solid #555', borderRadius: '20px', cursor: 'pointer' },
    autoInfo: { color: '#ccc', fontSize: '13px', marginTop: '10px' },
    select: { width: '100%', padding: '10px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px', marginTop: '8px' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' },
    orderCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    orderHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' },
    status: { fontSize: '14px' },
    orderTime: { color: '#666', fontSize: '12px' },
    itemRow: { display: 'flex', justifyContent: 'space-between', padding: '5px 0', color: '#ccc', fontSize: '14px' },
    sourceTag: { color: '#ff9800', fontSize: '12px', marginTop: '5px' },
    totalRow: { display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid #333', color: '#e94560', fontWeight: 'bold' }
};

export default OrderHistory;