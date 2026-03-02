import DashboardNav from '../components/DashboardNav';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../api';

function Dashboard() {
    const [dashboard, setDashboard] = useState(null);
    const [orders, setOrders] = useState([]);
    const [serviceRequests, setServiceRequests] = useState([]);
    const [paymentRequests, setPaymentRequests] = useState([]);
    const [bierdeckel, setBierdeckel] = useState([]);
    const [activeTab, setActiveTab] = useState('tables');
    const restaurantId = localStorage.getItem('restaurant_id');
    const navigate = useNavigate();

    useEffect(() => {
        loadAll();
        const interval = setInterval(loadAll, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadAll = async () => {
        try {
            const [dashRes, orderRes, serviceRes, paymentRes, bierdeckelRes] = await Promise.all([
                API.get(`/restaurant/${restaurantId}/dashboard`),
                API.get(`/restaurant/${restaurantId}/orders`),
                API.get(`/restaurant/${restaurantId}/service-requests`),
                API.get(`/restaurant/${restaurantId}/payment-requests`),
                API.get(`/restaurant/${restaurantId}/bierdeckel`)
            ]);
            setDashboard(dashRes.data);
            setOrders(orderRes.data);
            setServiceRequests(serviceRes.data);
            setPaymentRequests(paymentRes.data);
            setBierdeckel(bierdeckelRes.data);
        } catch (err) {
            console.error(err);
        }
    };

    const closeSession = async (sessionId) => {
        if (window.confirm('Session wirklich schließen?')) {
            await API.put(`/session/${sessionId}/close`);
            loadAll();
        }   
    };

    const confirmPayment = async (paymentId) => {
        await API.put(`/payment/${paymentId}/confirm`);
        loadAll();
    };

    const updateOrderStatus = async (orderId, status) => {
        await API.put(`/order/${orderId}/status/${status}`);
        loadAll();
    };

    const updateServiceStatus = async (requestId, status) => {
        await API.put(`/service-request/${requestId}/status/${status}`);
        loadAll();
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
    };

    const statusColors = {
        empty: '#e94560',
        low: '#ff9800',
        half: '#ffeb3b',
        full: '#4CAF50'
    };

    const statusLabels = {
        empty: 'Leer',
        low: 'Wenig',
        half: 'Halb',
        full: 'Voll'
    };

    return (
        <>
            <DashboardNav />
            <div style={styles.container}>
                <div style={styles.header}>
                    <h1 style={styles.title}>🍺 {dashboard?.restaurant || 'Dashboard'}</h1>
                </div>

                <div style={styles.tabs}>
                    {['tables', 'orders', 'service', 'payments', 'bierdeckel'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={activeTab === tab ? styles.activeTab : styles.tab}
                        >
                            {tab === 'tables' && `🪑 Tische`}
                            {tab === 'orders' && `📋 Bestellungen (${orders.length})`}
                            {tab === 'service' && `🔔 Service (${serviceRequests.length})`}
                            {tab === 'payments' && `💳 Zahlungen (${paymentRequests.length})`}
                            {tab === 'bierdeckel' && `🍺 Füllstand`}
                        </button>
                    ))}
                </div>

                <div style={styles.content}>
                    {activeTab === 'tables' && dashboard && (
                        <div style={styles.grid}>
                            {dashboard.tables.map(table => (
                                <div key={table.table_id} style={{
                                    ...styles.tableCard,
                                    borderColor: table.active_guests > 0 ? '#4CAF50' : '#333'
                                }}>
                                    <h3>Tisch {table.table_number}</h3>
                                    <p>👥 {table.active_guests} Gäste</p>
                                    {table.sessions.map(s => (
                                        <div key={s.session_id} style={styles.sessionInfo}>
                                            <p>📋 {s.open_orders} offene Bestellungen</p>
                                            <p>💰 {s.total.toFixed(2)} € / Bezahlt: {s.paid.toFixed(2)} €</p>
                                            <p>🔔 {s.open_service_requests} Anfragen</p>
                                            <button
                                                onClick={() => closeSession(s.session_id)}
                                                style={styles.closeSessionButton}
                                            >
                                                ❌ Session schließen
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'orders' && (
                        <div>
                            {orders.length === 0 ? (
                                <p style={styles.empty}>Keine offenen Bestellungen</p>
                            ) : (
                                orders.map(order => (
                                    <div key={order.order_id} style={styles.orderCard}>
                                        <div style={styles.orderHeader}>
                                            <span>🪑 Tisch {order.table_number}</span>
                                            <span style={styles.orderTotal}>{order.total.toFixed(2)} €</span>
                                        </div>
                                        {order.items.map((item, i) => (
                                            <p key={i} style={styles.orderItem}>{item.quantity}x {item.name}</p>
                                        ))}
                                        <p style={styles.orderTime}>{order.created_at}</p>
                                        <div style={styles.buttonRow}>
                                            {order.status === 'pending' && (
                                                <button onClick={() => updateOrderStatus(order.order_id, 'preparing')} style={styles.prepareButton}>
                                                    👨‍🍳 Zubereiten
                                                </button>
                                            )}
                                            {order.status === 'preparing' && (
                                                <button onClick={() => updateOrderStatus(order.order_id, 'delivered')} style={styles.deliverButton}>
                                                    ✅ Geliefert
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'service' && (
                        <div>
                            {serviceRequests.length === 0 ? (
                                <p style={styles.empty}>Keine offenen Anfragen</p>
                            ) : (
                                serviceRequests.map(req => (
                                    <div key={req.request_id} style={styles.orderCard}>
                                        <div style={styles.orderHeader}>
                                            <span>🪑 Tisch {req.table_number}</span>
                                            <span style={{ color: '#ff9800' }}>{req.request_type}</span>
                                        </div>
                                        {req.message && <p style={styles.orderItem}>{req.message}</p>}
                                        <p style={styles.orderTime}>{req.created_at}</p>
                                        <div style={styles.buttonRow}>
                                            {req.status === 'open' && (
                                                <button onClick={() => updateServiceStatus(req.request_id, 'in_progress')} style={styles.prepareButton}>
                                                    🏃 In Bearbeitung
                                                </button>
                                            )}
                                            {req.status === 'in_progress' && (
                                                <button onClick={() => updateServiceStatus(req.request_id, 'done')} style={styles.deliverButton}>
                                                    ✅ Erledigt
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'payments' && (
                        <div>
                            {paymentRequests.length === 0 ? (
                                <p style={styles.empty}>Keine Zahlungswünsche</p>
                            ) : (
                                paymentRequests.map(req => (
                                    <div key={req.payment_id} style={styles.orderCard}>
                                        <div style={styles.orderHeader}>
                                            <span>🪑 Tisch {req.table_number}</span>
                                            <span style={styles.orderTotal}>{req.amount.toFixed(2)} €</span>
                                        </div>
                                        <p style={styles.orderTime}>{req.created_at}</p>
                                        <button
                                            onClick={() => confirmPayment(req.payment_id)}
                                            style={styles.deliverButton}
                                        >
                                            ✅ Als bezahlt bestätigen
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'bierdeckel' && (
                        <div style={styles.grid}>
                            {bierdeckel.length === 0 ? (
                                <p style={styles.empty}>Keine Bierdeckel-Daten</p>
                            ) : (
                                bierdeckel.map(b => (
                                    <div key={b.table_id} style={styles.bierdeckelCard}>
                                        <h3>Tisch {b.table_number}</h3>
                                        <div style={{
                                            ...styles.statusDot,
                                            background: statusColors[b.status] || '#666'
                                        }}></div>
                                        <p style={{ color: statusColors[b.status] || '#666' }}>
                                            {statusLabels[b.status] || b.status}
                                        </p>
                                        <p style={styles.weight}>{b.weight}g</p>
                                        <p style={styles.orderTime}>{b.last_updated}</p>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 20px', borderBottom: '1px solid #333' },
    title: { margin: 0, fontSize: '20px' },
    logoutButton: { background: '#333', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' },
    tabs: { display: 'flex', overflowX: 'auto', borderBottom: '1px solid #333', padding: '0 10px' },
    tab: { background: 'none', color: '#888', border: 'none', padding: '12px 15px', cursor: 'pointer', whiteSpace: 'nowrap', fontSize: '14px' },
    activeTab: { background: 'none', color: '#e94560', border: 'none', borderBottom: '2px solid #e94560', padding: '12px 15px', cursor: 'pointer', whiteSpace: 'nowrap', fontSize: '14px' },
    content: { padding: '20px' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px' },
    tableCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', border: '2px solid #333' },
    sessionInfo: { borderTop: '1px solid #333', paddingTop: '10px', marginTop: '10px', fontSize: '13px', color: '#ccc' },
    orderCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    orderHeader: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' },
    orderTotal: { color: '#e94560', fontWeight: 'bold' },
    orderItem: { margin: '5px 0', color: '#ccc' },
    orderTime: { color: '#666', fontSize: '12px' },
    buttonRow: { display: 'flex', gap: '10px', marginTop: '10px' },
    prepareButton: { flex: 1, padding: '10px', background: '#ff9800', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    deliverButton: { flex: 1, padding: '10px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    bierdeckelCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', textAlign: 'center' },
    statusDot: { width: '20px', height: '20px', borderRadius: '50%', margin: '10px auto' },
    weight: { color: '#888', fontSize: '14px' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' },
    navButton: { background: '#1a1a2e', color: 'white', border: '1px solid #333', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' },
    closeSessionButton: { marginTop: '8px', padding: '6px 12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', width: '100%' }
    
};

export default Dashboard;