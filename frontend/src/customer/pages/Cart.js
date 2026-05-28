import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../../api';

function Cart() {
    const [cart, setCart] = useState([]);
    const [orderSent, setOrderSent] = useState(false);
    const [showService, setShowService] = useState(false);
    const navigate = useNavigate();
    const sessionId = localStorage.getItem('session_id');

    useEffect(() => {
        const savedCart = JSON.parse(localStorage.getItem('cart') || '[]');
        setCart(savedCart);
    }, []);

    const updateQuantity = (itemId, change) => {
        let newCart = cart.map(item =>
            item.menu_item_id === itemId
                ? { ...item, quantity: item.quantity + change }
                : item
        ).filter(item => item.quantity > 0);
        setCart(newCart);
        localStorage.setItem('cart', JSON.stringify(newCart));
    };

    const getTotal = () => cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const sendOrder = async () => {
        try {
            const items = cart.map(item => ({
                menu_item_id: item.menu_item_id,
                quantity: item.quantity
            }));
            await API.post(`/session/${sessionId}/order`, { items });
            localStorage.setItem('cart', '[]');
            setCart([]);
            setOrderSent(true);
            setTimeout(() => navigate('/orders'), 2000);
        } catch (err) {
            alert('Fehler beim Bestellen');
        }
    };

    const callService = async (type) => {
        try {
            await API.post(`/session/${sessionId}/service-request`, {
                request_type: type,
                message: ''
            });
            alert('Service-Anfrage gesendet!');
            setShowService(false);
        } catch (err) {
            alert('Fehler beim Senden');
        }
    };

    if (orderSent) {
        return (
            <div style={styles.container}>
                <div style={styles.success}>
                    <h2>✅ Bestellung aufgegeben!</h2>
                    <p>Weiterleitung zu Bestellungen...</p>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>🛒 Warenkorb</h1>

            {cart.length === 0 ? (
                <p style={styles.empty}>Warenkorb ist leer</p>
            ) : (
                <>
                    {cart.map(item => (
                        <div key={item.menu_item_id} style={styles.cartItem}>
                            <div>
                                <h3 style={styles.itemName}>{item.name}</h3>
                                <p style={styles.itemPrice}>{(item.price * item.quantity).toFixed(2)} €</p>
                            </div>
                            <div style={styles.quantity}>
                                <button onClick={() => updateQuantity(item.menu_item_id, -1)} style={styles.qtyButton}>-</button>
                                <span style={styles.qtyText}>{item.quantity}</span>
                                <button onClick={() => updateQuantity(item.menu_item_id, 1)} style={styles.qtyButton}>+</button>
                            </div>
                        </div>
                    ))}

                    <div style={styles.total}>
                        <h2>Gesamt: {getTotal().toFixed(2)} €</h2>
                    </div>

                    <button onClick={sendOrder} style={styles.orderButton}>
                        Jetzt bestellen
                    </button>
                </>
            )}

            <div style={{ height: '80px' }}></div>

            <button onClick={() => setShowService(true)} style={styles.serviceFloating}>🔔</button>

            {showService && (
                <div style={styles.serviceOverlay}>
                    <div style={styles.serviceModal}>
                        <h3>Service rufen</h3>
                        <button onClick={() => callService('waiter')} style={styles.serviceButton}>🧑‍🍳 Kellner rufen</button>
                        <button onClick={() => callService('napkins')} style={styles.serviceButton}>🧻 Servietten</button>
                        <button onClick={() => callService('other')} style={styles.serviceButton}>❓ Sonstiges</button>
                        <button onClick={() => setShowService(false)} style={styles.serviceClose}>Schließen</button>
                    </div>
                </div>
            )}
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    empty: { textAlign: 'center', color: '#888', marginTop: '50px' },
    cartItem: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px'
    },
    itemName: { margin: '0 0 5px 0' },
    itemPrice: { margin: 0, color: '#e94560' },
    quantity: { display: 'flex', alignItems: 'center', gap: '10px' },
    qtyButton: {
        background: '#333', color: 'white', border: 'none', borderRadius: '50%',
        width: '30px', height: '30px', fontSize: '16px', cursor: 'pointer'
    },
    qtyText: { fontSize: '18px', fontWeight: 'bold' },
    total: { textAlign: 'center', marginTop: '20px', color: '#e94560' },
    orderButton: {
        width: '100%', padding: '15px', background: '#e94560', color: 'white',
        border: 'none', borderRadius: '10px', fontSize: '18px', cursor: 'pointer', marginTop: '10px'
    },
    success: { textAlign: 'center', marginTop: '100px' },
    serviceFloating: { position: 'fixed', bottom: '80px', right: '20px', width: '55px', height: '55px', borderRadius: '50%', background: '#e94560', color: 'white', border: 'none', fontSize: '24px', cursor: 'pointer', zIndex: 998, boxShadow: '0 2px 10px rgba(233,69,96,0.4)' },
    serviceOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    serviceModal: { background: '#1a1a2e', padding: '25px', borderRadius: '15px', width: '280px', display: 'flex', flexDirection: 'column', gap: '10px' },
    serviceButton: { padding: '14px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', textAlign: 'left' },
    serviceClose: { padding: '12px', background: '#333', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', marginTop: '5px' }
};

export default Cart;