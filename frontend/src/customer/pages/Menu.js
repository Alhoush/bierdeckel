import React, { useEffect, useState } from 'react';
import API from '../../api';

function Menu() {
    const [menu, setMenu] = useState({});
    const [cart, setCart] = useState([]);
    const [showService, setShowService] = useState(false);
    const sessionId = localStorage.getItem('session_id');
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadMenu();
        const savedCart = JSON.parse(localStorage.getItem('cart') || '[]');
        setCart(savedCart);
    }, []);

    const loadMenu = async () => {
        try {
            const res = await API.get(`/restaurant/${restaurantId}/menu`);
            setMenu(res.data);
        } catch (err) {
            console.error('Menü laden fehlgeschlagen:', err);
        }
    };

    const addToCart = (item) => {
        const existing = cart.find(c => c.menu_item_id === item.id);
        let newCart;
        if (existing) {
            newCart = cart.map(c =>
                c.menu_item_id === item.id
                    ? { ...c, quantity: c.quantity + 1 }
                    : c
            );
        } else {
            newCart = [...cart, { menu_item_id: item.id, name: item.name, price: item.price, quantity: 1 }];
        }
        setCart(newCart);
        localStorage.setItem('cart', JSON.stringify(newCart));
    };

    const getItemCount = (itemId) => {
        const item = cart.find(c => c.menu_item_id === itemId);
        return item ? item.quantity : 0;
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

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>🍺 Speisekarte</h1>
            <p style={styles.tableInfo}>Tisch {localStorage.getItem('table_number')}</p>

            {Object.keys(menu).length === 0 && (
                <p style={styles.empty}>Menü ist leer</p>
            )}

            {Object.entries(menu).map(([category, items]) => (
                <div key={category} style={styles.category}>
                    <h2 style={styles.categoryTitle}>{category}</h2>
                    {items.map(item => (
                        <div key={item.id} style={styles.menuItem}>
                            <div>
                                <h3 style={styles.itemName}>{item.name}</h3>
                                <p style={styles.itemDesc}>{item.description}</p>
                                <p style={styles.itemPrice}>{item.price.toFixed(2)} €</p>
                            </div>
                            <button onClick={() => addToCart(item)} style={styles.addButton}>
                                + {getItemCount(item.id) > 0 && `(${getItemCount(item.id)})`}
                            </button>
                        </div>
                    ))}
                </div>
            ))}

            <div style={{ height: '100px' }}></div>
            {/* Kellner rufen Button */}
            <button onClick={() => setShowService(true)} style={styles.serviceFloating}>🔔</button>

            {showService && (
                <div style={styles.serviceOverlay}>
                    <div style={styles.serviceModal}>
                        <h3>Service rufen</h3>
                        <button onClick={() => callService('waiter')} style={styles.serviceButton}>🧑‍🍳 Servicekraft rufen</button>
                        <button onClick={() => setShowService(false)} style={styles.serviceClose}>Schließen</button>
                    </div>
                </div>
            )}
            
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center', marginBottom: '5px' },
    tableInfo: { textAlign: 'center', color: '#888', marginBottom: '20px' },
    category: { marginBottom: '20px' },
    categoryTitle: { color: '#e94560', borderBottom: '1px solid #333', paddingBottom: '8px' },
    menuItem: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px'
    },
    itemName: { margin: '0 0 5px 0', fontSize: '16px' },
    itemDesc: { margin: '0 0 5px 0', color: '#888', fontSize: '13px' },
    itemPrice: { margin: 0, color: '#e94560', fontWeight: 'bold' },
    addButton: {
        background: '#e94560', color: 'white', border: 'none', borderRadius: '50%',
        width: '40px', height: '40px', fontSize: '20px', cursor: 'pointer'
    },
    serviceFloating: { position: 'fixed', bottom: '80px', right: '20px', width: '55px', height: '55px', borderRadius: '50%', background: '#e94560', color: 'white', border: 'none', fontSize: '24px', cursor: 'pointer', zIndex: 998, boxShadow: '0 2px 10px rgba(233,69,96,0.4)' },
    serviceOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    serviceModal: { background: '#1a1a2e', padding: '25px', borderRadius: '15px', width: '280px', display: 'flex', flexDirection: 'column', gap: '10px' },
    serviceButton: { padding: '14px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', textAlign: 'left' },
    serviceClose: { padding: '12px', background: '#333', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', marginTop: '5px' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' }
};

export default Menu;