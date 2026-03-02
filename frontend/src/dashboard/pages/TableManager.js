import React, { useEffect, useState } from 'react';
import API from '../../api';
import DashboardNav from '../components/DashboardNav';

function TableManager() {
    const [tables, setTables] = useState([]);
    const [tableNumber, setTableNumber] = useState('');
    const [seats, setSeats] = useState('4');
    const [bdLabel, setBdLabel] = useState('');
    const [selectedTable, setSelectedTable] = useState(null);
    const [bierdeckel, setBierdeckel] = useState([]);
    const [qrImage, setQrImage] = useState(null);
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadTables();
    }, []);

    const loadTables = async () => {
        const res = await API.get(`/restaurant/${restaurantId}/tables`);
        setTables(res.data);
    };

    const addTable = async () => {
        if (!tableNumber) return alert('Tischnummer eingeben');
        try {
            await API.post(`/restaurant/${restaurantId}/table`, {
                table_number: parseInt(tableNumber),
                seats: parseInt(seats)
            });
            setTableNumber('');
            setSeats('4');
            loadTables();
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const selectTable = async (table) => {
        setSelectedTable(table);
        const res = await API.get(`/table/${table.id}/bierdeckel`);
        setBierdeckel(res.data);
    };

    const addBierdeckel = async () => {
        if (!bdLabel || !selectedTable) return alert('Label eingeben');
        try {
            await API.post(`/table/${selectedTable.id}/bierdeckel`, { label: bdLabel });
            setBdLabel('');
            selectTable(selectedTable);
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const showQR = async (bierdeckelId) => {
        const res = await API.get(`/bierdeckel/${bierdeckelId}/qr`);
        setQrImage(res.data);
    };

    return (
        <>
            <DashboardNav />
            <div style={styles.container}>
                <h1 style={styles.title}>🪑 Tische & Bierdeckel verwalten</h1>

                <div style={styles.addForm}>
                    <h3 style={styles.formTitle}>Neuer Tisch</h3>
                    <div style={styles.inputRow}>
                        <input placeholder="Tischnummer" type="number" value={tableNumber} onChange={e => setTableNumber(e.target.value)} style={styles.input} />
                        <input placeholder="Plätze" type="number" value={seats} onChange={e => setSeats(e.target.value)} style={styles.inputSmall} />
                        <button onClick={addTable} style={styles.addButton}>+ Tisch</button>
                    </div>
                </div>

                <div style={styles.layout}>
                    <div style={styles.tableList}>
                        <h3>Tische</h3>
                        {tables.map(table => (
                            <div
                                key={table.id}
                                onClick={() => selectTable(table)}
                                style={{
                                    ...styles.tableCard,
                                    borderColor: selectedTable?.id === table.id ? '#e94560' : '#333'
                                }}
                            >
                                <h3>Tisch {table.table_number}</h3>
                                <p>{table.seats} Plätze • {table.bierdeckel_count} Bierdeckel</p>
                            </div>
                        ))}
                    </div>

                    <div style={styles.bdList}>
                        {selectedTable ? (
                            <>
                                <h3>Bierdeckel – Tisch {selectedTable.table_number}</h3>
                                <div style={styles.inputRow}>
                                    <input placeholder="Label (z.B. BD-001)" value={bdLabel} onChange={e => setBdLabel(e.target.value)} style={styles.input} />
                                    <button onClick={addBierdeckel} style={styles.addButton}>+ Bierdeckel</button>
                                </div>

                                {bierdeckel.map(bd => (
                                    <div key={bd.id} style={styles.bdCard}>
                                        <div>
                                            <h4 style={styles.bdLabel}>{bd.label}</h4>
                                            <p style={styles.bdStatus}>Status: {bd.status} • {bd.weight}g</p>
                                        </div>
                                        <button onClick={() => showQR(bd.id)} style={styles.qrButton}>📱 QR</button>
                                    </div>
                                ))}
                            </>
                        ) : (
                            <p style={styles.empty}>Tisch auswählen um Bierdeckel zu sehen</p>
                        )}
                    </div>
                </div>

                {qrImage && (
                    <div style={styles.qrModal}>
                        <div style={styles.qrContent}>
                            <h3>{qrImage.label} – Tisch {qrImage.table_number}</h3>
                            <img src={qrImage.qr_code_image} alt="QR Code" style={styles.qrImg} />
                            <p style={styles.qrUrl}>{qrImage.qr_code_url}</p>
                            <button onClick={() => setQrImage(null)} style={styles.closeButton}>Schließen</button>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    addForm: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', marginBottom: '20px' },
    formTitle: { margin: '0 0 15px 0', color: '#e94560' },
    inputRow: { display: 'flex', gap: '10px' },
    input: { flex: 1, padding: '12px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px' },
    inputSmall: { width: '80px', padding: '12px', background: '#0f0f23', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px' },
    addButton: { padding: '12px 20px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', whiteSpace: 'nowrap' },
    layout: { display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' },
    tableList: {},
    tableCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', border: '2px solid #333', marginBottom: '10px', cursor: 'pointer' },
    bdList: {},
    bdCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    bdLabel: { margin: '0 0 5px 0' },
    bdStatus: { margin: 0, color: '#888', fontSize: '13px' },
    qrButton: { background: '#333', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' },
    qrModal: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
    qrContent: { background: '#1a1a2e', padding: '30px', borderRadius: '15px', textAlign: 'center' },
    qrImg: { width: '250px', height: '250px', margin: '15px 0' },
    qrUrl: { color: '#888', fontSize: '12px', wordBreak: 'break-all', marginBottom: '15px' },
    closeButton: { padding: '10px 30px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' }
};

export default TableManager;