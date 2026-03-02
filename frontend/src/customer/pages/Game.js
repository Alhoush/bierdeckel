import React, { useState, useEffect } from 'react';
import API from '../../api';

function Game() {
    const [openGames, setOpenGames] = useState([]);
    const [myGame, setMyGame] = useState(null);
    const [gameStatus, setGameStatus] = useState(null);
    const [joinRequests, setJoinRequests] = useState([]);
    const [menuItems, setMenuItems] = useState([]);
    const [selectedDrink, setSelectedDrink] = useState('');
    const [view, setView] = useState('list');
    const sessionId = localStorage.getItem('session_id');
    const restaurantId = localStorage.getItem('restaurant_id');

    useEffect(() => {
        loadOpenGames();
        loadMenu();
    }, []);

    useEffect(() => {
        if (myGame) {
            const interval = setInterval(() => {
                loadGameStatus(myGame);
                loadJoinRequests(myGame);
            }, 3000);
            return () => clearInterval(interval);
        }
    }, [myGame]);

    const loadOpenGames = async () => {
        const res = await API.get(`/restaurant/${restaurantId}/games`);
        setOpenGames(res.data);
    };

    const loadMenu = async () => {
        const res = await API.get(`/restaurant/${restaurantId}/menu`);
        const allItems = Object.values(res.data).flat();
        setMenuItems(allItems);
    };

    const loadGameStatus = async (gameId) => {
        try {
            const res = await API.get(`/game/${gameId}`);
            setGameStatus(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const loadJoinRequests = async (gameId) => {
        try {
            const res = await API.get(`/game/${gameId}/requests`);
            setJoinRequests(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const createGame = async () => {
        if (!selectedDrink) return alert('Getränk auswählen');
        try {
            const res = await API.post(`/session/${sessionId}/game/create`, {
                menu_item_id: selectedDrink
            });
            setMyGame(res.data.game_id);
            setView('game');
            loadGameStatus(res.data.game_id);
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const requestJoin = async (gameId) => {
        try {
            await API.post(`/game/${gameId}/request-join/${sessionId}`);
            setMyGame(gameId);
            setView('game');
            loadGameStatus(gameId);
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const approvePlayer = async (playerId) => {
        await API.put(`/game/${myGame}/approve/${playerId}`);
        loadJoinRequests(myGame);
        loadGameStatus(myGame);
    };

    const declinePlayer = async (playerId) => {
        await API.put(`/game/${myGame}/decline/${playerId}`);
        loadJoinRequests(myGame);
    };

    const startGame = async () => {
        try {
            await API.put(`/game/${myGame}/start`);
            loadGameStatus(myGame);
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    const finishDrink = async () => {
        try {
            const res = await API.post(`/game/${myGame}/finish`, { session_id: sessionId });
            loadGameStatus(myGame);
        } catch (err) {
            alert(err.response?.data?.detail || 'Fehler');
        }
    };

    // Liste der offenen Spiele
    if (view === 'list') {
        return (
            <div style={styles.container}>
                <h1 style={styles.title}>🎮 Trinkspiel</h1>

                <div style={styles.section}>
                    <h3 style={styles.subtitle}>Neues Spiel erstellen</h3>
                    <select
                        value={selectedDrink}
                        onChange={e => setSelectedDrink(e.target.value)}
                        style={styles.select}
                    >
                        <option value="">Getränk auswählen...</option>
                        {menuItems.map(item => (
                            <option key={item.id} value={item.id}>
                                {item.name} - {item.price.toFixed(2)} €
                            </option>
                        ))}
                    </select>
                    <button onClick={createGame} style={styles.createButton}>
                        🎮 Spiel erstellen
                    </button>
                </div>

                <div style={styles.section}>
                    <h3 style={styles.subtitle}>Offene Spiele</h3>
                    {openGames.length === 0 ? (
                        <p style={styles.empty}>Keine offenen Spiele</p>
                    ) : (
                        openGames.map(game => (
                            <div key={game.game_id} style={styles.gameCard}>
                                <div>
                                    <p>🪑 Tisch {game.table_number}</p>
                                    <p style={styles.playerCount}>👥 {game.player_count} Spieler</p>
                                </div>
                                {game.creator_session_id !== sessionId && (
                                    <button onClick={() => requestJoin(game.game_id)} style={styles.joinButton}>
                                        Beitreten
                                    </button>
                                )}
                                {game.creator_session_id === sessionId && (
                                    <button onClick={() => { setMyGame(game.game_id); setView('game'); loadGameStatus(game.game_id); }} style={styles.joinButton}>
                                        Öffnen
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                    <button onClick={loadOpenGames} style={styles.refreshButton}>🔄 Aktualisieren</button>
                </div>

                <div style={{ height: '100px' }}></div>
            </div>
        );
    }

    // Spiel-Ansicht
    return (
        <div style={styles.container}>
            <h1 style={styles.title}>🎮 Trinkspiel</h1>

            <button onClick={() => { setView('list'); setMyGame(null); setGameStatus(null); }} style={styles.backButton}>
                ← Zurück
            </button>

            {gameStatus && (
                <div style={styles.section}>
                    <div style={styles.statusCard}>
                        <h3>Status: {gameStatus.status === 'waiting' ? '⏳ Wartet' : gameStatus.status === 'active' ? '🏁 Läuft!' : '🏆 Beendet'}</h3>
                        <p style={styles.gameId}>Spiel-ID: {gameStatus.game_id}</p>
                    </div>

                    {/* Beitrittsanfragen (nur Ersteller sieht das) */}
                    {gameStatus.creator_session_id === sessionId && gameStatus.status === 'waiting' && (
                        <div style={styles.requestSection}>
                            <h3>📩 Beitrittsanfragen</h3>
                            {joinRequests.length === 0 ? (
                                <p style={styles.empty}>Keine Anfragen</p>
                            ) : (
                                joinRequests.map(req => (
                                    <div key={req.player_id} style={styles.requestCard}>
                                        <span>🪑 Tisch {req.table_number}</span>
                                        <div style={styles.buttonRow}>
                                            <button onClick={() => approvePlayer(req.player_id)} style={styles.approveButton}>✅</button>
                                            <button onClick={() => declinePlayer(req.player_id)} style={styles.declineButton}>❌</button>
                                        </div>
                                    </div>
                                ))
                            )}

                            {gameStatus.players.length >= 2 && (
                                <button onClick={startGame} style={styles.startButton}>
                                    🏁 Spiel starten ({gameStatus.players.length} Spieler)
                                </button>
                            )}
                        </div>
                    )}

                    {/* Spieler-Liste */}
                    <div style={styles.playerSection}>
                        <h3>👥 Spieler</h3>
                        {gameStatus.players.map(p => (
                            <div key={p.session_id} style={styles.playerCard}>
                                <span>
                                    🪑 Tisch {p.table_number}
                                    {p.session_id === sessionId && ' (Du)'}
                                </span>
                                <span style={{ color: p.finished ? '#4CAF50' : '#ff9800' }}>
                                    {p.finished ? '✅ Fertig' : '⏳ Trinkt...'}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Trinken-Button */}
                    {gameStatus.status === 'active' && (
                        <button onClick={finishDrink} style={styles.drinkButton}>
                            🍺 Fertig getrunken!
                        </button>
                    )}

                    {/* Ergebnis */}
                    {gameStatus.status === 'finished' && gameStatus.loser_session_id && (
                        <div style={styles.resultCard}>
                            {gameStatus.loser_session_id === sessionId
                                ? <h2>😅 Du hast verloren! Du zahlst die Getränke!</h2>
                                : <h2>🎉 Du hast gewonnen! Prost!</h2>
                            }
                        </div>
                    )}
                </div>
            )}

            <div style={{ height: '100px' }}></div>
        </div>
    );
}

const styles = {
    container: { background: '#0f0f23', minHeight: '100vh', color: 'white', padding: '20px' },
    title: { textAlign: 'center' },
    section: { marginTop: '20px' },
    subtitle: { color: '#e94560' },
    select: { width: '100%', padding: '12px', background: '#1a1a2e', color: 'white', border: '1px solid #333', borderRadius: '8px', fontSize: '14px', marginBottom: '10px' },
    createButton: { width: '100%', padding: '15px', background: '#e94560', color: 'white', border: 'none', borderRadius: '10px', fontSize: '16px', cursor: 'pointer' },
    gameCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1a1a2e', padding: '15px', borderRadius: '10px', marginBottom: '10px' },
    playerCount: { color: '#888', fontSize: '13px', margin: 0 },
    joinButton: { background: '#e94560', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer' },
    refreshButton: { width: '100%', padding: '10px', background: '#333', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', marginTop: '10px' },
    backButton: { background: '#333', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', marginBottom: '15px' },
    statusCard: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', textAlign: 'center' },
    gameId: { color: '#888', fontSize: '12px' },
    requestSection: { marginTop: '20px' },
    requestCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1a1a2e', padding: '12px', borderRadius: '8px', marginBottom: '8px' },
    buttonRow: { display: 'flex', gap: '8px' },
    approveButton: { background: '#4CAF50', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
    declineButton: { background: '#e94560', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
    startButton: { width: '100%', padding: '15px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '10px', fontSize: '16px', cursor: 'pointer', marginTop: '15px' },
    playerSection: { marginTop: '20px' },
    playerCard: { display: 'flex', justifyContent: 'space-between', background: '#1a1a2e', padding: '12px', borderRadius: '8px', marginBottom: '8px' },
    drinkButton: { width: '100%', padding: '20px', background: '#e94560', color: 'white', border: 'none', borderRadius: '10px', fontSize: '20px', cursor: 'pointer', marginTop: '20px' },
    resultCard: { background: '#1a1a2e', padding: '20px', borderRadius: '10px', textAlign: 'center', marginTop: '20px' },
    empty: { color: '#888' }
};

export default Game;