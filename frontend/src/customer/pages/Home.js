import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../../api';

function Home() {
    const { restaurantId, bierdeckelId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function createSession() {
            try {
                const res = await API.post(`/r/${restaurantId}/bd/${bierdeckelId}/scan`);
                localStorage.setItem('session_id', res.data.session_id);
                localStorage.setItem('restaurant_id', res.data.restaurant_id);
                localStorage.setItem('bierdeckel_id', res.data.bierdeckel_id);
                localStorage.setItem('table_number', res.data.table_number);
                navigate('/menu');
            } catch (err) {
                setError('QR-Code ungültig oder Bierdeckel nicht gefunden');
            }
            setLoading(false);
        }
        createSession();
    }, [restaurantId, bierdeckelId, navigate]);

    if (loading) return <div style={styles.container}><h2>⏳ Wird geladen...</h2></div>;
    if (error) return <div style={styles.container}><h2>❌ {error}</h2></div>;
    return null;
}

const styles = {
    container: {
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        height: '100vh', background: '#0f0f23', color: 'white'
    }
};

export default Home;