import React, { useEffect, useState } from 'react';
import API from '../../api';

function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState([]);
    const [sortBy, setSortBy] = useState('wins');
    const [myStats, setMyStats] = useState(null);
    const restaurantId = localStorage.getItem('restaurant_id');
    const customerId = localStorage.getItem('customer_id');

    useEffect(() => {
        loadLeaderboard();
        if (customerId) loadMyStats();
    }, [sortBy]);

    const loadLeaderboard = async () => {
        const res = await API.get(`/restaurant/${restaurantId}/leaderboard?sort_by=${sortBy}`);
        setLeaderboard(res.data);
    };

    const loadMyStats = async () => {
        try {
            const res = await API.get(`/customer/${customerId}/stats`);
            const stat = res.data.find(s => s.restaurant_id === restaurantId);
            setMyStats(stat);
        } catch (err) {}
    };

    const getMedal = (rank) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>🏆 Rangliste</h1>

            <div style={styles.sortRow}>
                <button onClick={() => setSortBy('wins')} style={sortBy === 'wins' ? styles.activeSort : styles.sortButton}>Meiste Siege</button>
                <button onClick={() => setSortBy('winrate')} style={sortBy === 'winrate' ? styles.activeSort : styles.sortButton}>Beste Win-Rate</button>
            </div>

            {/* Eigene Stats */}
            {myStats && (
                <div style={styles.myStatsCard}>
                    <h3 style={styles.myStatsTitle}>Deine Statistik</h3>
                    <div style={styles.statsRow}>
                        <div style={styles.statBox}>
                            <span style={styles.statNumber}>{myStats.games_played}</span>
                            <span style={styles.statLabel}>Spiele</span>
                        </div>
                        <div style={styles.statBox}>
                            <span style={{ ...styles.statNumber, color: '#4CAF50' }}>{myStats.games_won}</span>
                            <span style={styles.statLabel}>Siege</span>
                        </div>
                        <div style={styles.statBox}>
                            <span style={{ ...styles.statNumber, color: '#e94560' }}>{myStats.games_lost}</span>
                            <span style={styles.statLabel}>Niederlagen</span>
                        </div>
                        <div style={styles.statBox}>
                            <span style={styles.statNumber}>{myStats.win_rate}%</span>
                            <span style={styles.statLabel}>Win-Rate</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Rangliste */}
            {leaderboard.length === 0 ? (
                <p style={styles.empty}>Noch keine Spiele gespielt</p>
            ) : (
                leaderboard.map(player => (
                    <div key={player.customer_id} style={{
                        ...styles.playerCard,
                        borderColor: player.customer_id === customerId ? '#e94560' : '#333'
                    }}>
                        <div style={styles.rankSection}>
                            <span style={styles.rank}>{getMedal(player.rank)}</span>
                        </div>
                        <div style={styles.avatarSection}>
                            {player.avatar_url ? (
                                <img src={`http://127.0.0.1:8000${player.avatar_url}`} alt="" style={styles.avatar} />
                            ) : (
                                <div style={styles.avatarPlaceholder}>👤</div>
                            )}
                        </div>
                        <div style={styles.infoSection}>
                            <span style={styles.playerName}>
                                {player.display_name}
                                {player.customer_id === customerId && ' (Du)'}
                            </span>
                            <span style={styles.playerStats}>
                                {player.games_won}W / {player.games_lost}L • {player.win_rate}%
                            </span>
                        </div>
                        <div style={styles.winsSection}>
                            <span style={styles.winsNumber}>{sortBy === 'wins' ? player.games_won : `${player.win_rate}%`}</span>
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
    sortRow: { display: 'flex', gap: '10px', marginBottom: '20px' },
    sortButton: { flex: 1, padding: '10px', background: '#1a1a2e', color: '#888', border: '1px solid #333', borderRadius: '8px', cursor: 'pointer' },
    activeSort: { flex: 1, padding: '10px', background: '#e94560', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' },
    myStatsCard: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #e94560' },
    myStatsTitle: { color: '#e94560', margin: '0 0 10px 0', textAlign: 'center' },
    statsRow: { display: 'flex', justifyContent: 'space-around' },
    statBox: { display: 'flex', flexDirection: 'column', alignItems: 'center' },
    statNumber: { fontSize: '24px', fontWeight: 'bold', color: 'white' },
    statLabel: { fontSize: '11px', color: '#888' },
    empty: { color: '#888', textAlign: 'center', marginTop: '50px' },
    playerCard: { display: 'flex', alignItems: 'center', background: '#1a1a2e', padding: '12px', borderRadius: '10px', marginBottom: '8px', border: '2px solid #333', gap: '12px' },
    rankSection: { width: '35px', textAlign: 'center' },
    rank: { fontSize: '20px' },
    avatarSection: {},
    avatar: { width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover' },
    avatarPlaceholder: { width: '40px', height: '40px', borderRadius: '50%', background: '#333', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' },
    infoSection: { flex: 1, display: 'flex', flexDirection: 'column' },
    playerName: { fontWeight: 'bold', fontSize: '14px' },
    playerStats: { color: '#888', fontSize: '12px' },
    winsSection: { textAlign: 'right' },
    winsNumber: { fontSize: '20px', fontWeight: 'bold', color: '#e94560' }
};

export default Leaderboard;