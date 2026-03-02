import DashboardNav from '../components/DashboardNav';
import React, { useEffect, useState } from 'react';
import API from '../../api';

function MenuManager() {
    const [menu, setMenu] = useState({});
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [category, setCategory] = useState('');
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadMenu();
    }, []);

    const loadMenu = async () => {
        const res = await API.get(`/restaurant/${restaurantId}/menu`);
        setMenu(res.data);
    };

    const addItem = async () => {
        if (!name || !price || !category) return alert('Alle Felder ausfüllen');
        await API.post(`/restaurant/${restaurantId}/menu`, {
            name, description, price: parseFloat(price), category
        });
        setName(''); setDescription(''); setPrice(''); setCategory('');
        loadMenu();
    };

    const deleteItem = async (itemId) => {
        await API.delete(`/menu/${itemId}`);
        loadMenu();
    };

    const toggleAvailability = async (itemId, currentStatus) => {
        await API.put(`/menu/${itemId}`, { is_available: !currentStatus });
        loadMenu();
    };

    return (
        <>
            <DashboardNav />
            <div style={styles.container}>
                <h1 style={styles.title}>📋 Menü verwalten</h1>

                <div style={styles.addForm}>
                    <h3 style={styles.formTitle}>Neues Item</h3>
                    <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} style={styles.input} />
                    <input placeholder="Beschreibung" value={description} onChange={e => setDescription(e.target.value)} style={styles.input} />
                    <input placeholder="Preis" type="number" value={price} onChange={e => setPrice(e.target.value)} style={styles.input} />
                    <input placeholder="Kategorie (z.B. Bier)" value={category} onChange={e => setCategory(e.target.value)} style={styles.input} />
                    <button onClick={addItem} style={styles.addButton}>+ Hinzufügen</button>
                </div>

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
                                <div style={styles.actions}>
                                    <button onClick={() => deleteItem(item.id)} style={styles.deleteButton}>🗑️</button>
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    addForm: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', marginBottom: '20px' },
    formTitle: { margin: '0 0 15px 0', color: '#e94560' },
    input: { width: '100%', padding: '10px', marginBottom: '10px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px', boxSizing: 'border-box' },
    addButton: { width: '100%', padding: '12px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer' },
    category: { marginBottom: '20px' },
    categoryTitle: { color: '#e94560', borderBottom: '1px solid #333', paddingBottom: '8px' },
    menuItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    itemName: { margin: '0 0 5px 0' },
    itemDesc: { margin: '0 0 5px 0', color: '#888', fontSize: '13px' },
    itemPrice: { margin: 0, color: '#e94560' },
    actions: { display: 'flex', gap: '10px' },
    deleteButton: { background: '#333', border: 'none', padding: '8px 12px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' }
};

export default MenuManager;