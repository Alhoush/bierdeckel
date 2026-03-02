import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import API from '../../api';

function Navbar() {
    const location = useLocation();
    const [showService, setShowService] = useState(false);
    const sessionId = localStorage.getItem('session_id');

    const tabs = [
        { path: '/menu', label: '🍺', name: 'Menü' },
        { path: '/cart', label: '🛒', name: 'Warenkorb' },
        { path: '/orders', label: '📋', name: 'Bestellungen' },
        { path: '/payment', label: '💳', name: 'Bezahlen' },
        { path: '/drink', label: '🍻', name: 'Zusammen' },
        { path: '/game', label: '🎮', name: 'Spiel' },
    ];

    const sendServiceRequest = async (type, message) => {
        try {
            await API.post(`/session/${sessionId}/service-request`, {
                request_type: type,
                message: message
            });
            alert('✅ Anfrage gesendet!');
            setShowService(false);
        } catch (err) {
            alert('Fehler beim Senden');
        }
    };

    return (
        <>
            {showService && (
                <div style={styles.overlay}>
                    <div style={styles.modal}>
                        <h3 style={styles.modalTitle}>🔔 Service rufen</h3>
                        <button onClick={() => sendServiceRequest('waiter', 'Kellner bitte!')} style={styles.serviceButton}>
                            🧑‍🍳 Kellner rufen
                        </button>
                        <button onClick={() => sendServiceRequest('napkins', 'Servietten bitte')} style={styles.serviceButton}>
                            🧻 Servietten
                        </button>
                        <button onClick={() => sendServiceRequest('other', 'Sonstige Anfrage')} style={styles.serviceButton}>
                            ❓ Sonstiges
                        </button>
                        <button onClick={() => setShowService(false)} style={styles.closeButton}>
                            Schließen
                        </button>
                    </div>
                </div>
            )}

            <div style={styles.serviceTab}>
                <button onClick={() => setShowService(true)} style={styles.serviceMainButton}>
                    🔔 Service
                </button>
            </div>

            <nav style={styles.nav}>
                {tabs.map(tab => (
                    <Link
                        key={tab.path}
                        to={tab.path}
                        style={{
                            ...styles.tab,
                            color: location.pathname === tab.path ? '#e94560' : '#888'
                        }}
                    >
                        <span style={styles.icon}>{tab.label}</span>
                        <span style={styles.name}>{tab.name}</span>
                    </Link>
                ))}
            </nav>
        </>
    );
}

const styles = {
    nav: {
        position: 'fixed', bottom: 0, left: 0, right: 0,
        background: '#1a1a2e', display: 'flex', justifyContent: 'space-around',
        padding: '8px 0', borderTop: '1px solid #333'
    },
    tab: { textDecoration: 'none', textAlign: 'center', fontSize: '11px' },
    icon: { display: 'block', fontSize: '20px' },
    name: { display: 'block', marginTop: '2px' },
    serviceTab: {
        position: 'fixed', bottom: '65px', left: 0, right: 0,
        display: 'flex', justifyContent: 'center', padding: '5px'
    },
    serviceMainButton: {
        background: '#e94560', color: 'white', border: 'none',
        padding: '10px 30px', borderRadius: '20px', fontSize: '14px', cursor: 'pointer',
        boxShadow: '0 2px 10px rgba(233,69,96,0.3)'
    },
    overlay: {
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(0,0,0,0.8)', display: 'flex',
        justifyContent: 'center', alignItems: 'center', zIndex: 1000
    },
    modal: { background: '#1a1a2e', padding: '25px', borderRadius: '15px', width: '300px' },
    modalTitle: { textAlign: 'center', color: 'white', marginBottom: '20px' },
    serviceButton: {
        width: '100%', padding: '15px', background: '#0f0f23', color: 'white',
        border: '1px solid #333', borderRadius: '10px', fontSize: '16px',
        cursor: 'pointer', marginBottom: '10px'
    },
    closeButton: {
        width: '100%', padding: '12px', background: '#333', color: 'white',
        border: 'none', borderRadius: '10px', fontSize: '14px', cursor: 'pointer', marginTop: '5px'
    }
};

export default Navbar;