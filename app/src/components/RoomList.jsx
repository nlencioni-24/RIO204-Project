import { useState, useEffect } from 'react'
import RoomCard from './RoomCard'

function RoomList() {
    const [rooms, setRooms] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')

    useEffect(() => {
        fetch('/api/rooms')
            .then(res => {
                if (!res.ok) throw new Error('Erreur serveur')
                return res.json()
            })
            .then(data => {
                if (data.success) {
                    setRooms(data.rooms)
                } else {
                    throw new Error(data.error || 'Erreur inconnue')
                }
                setLoading(false)
            })
            .catch(err => {
                setError(err.message)
                setLoading(false)
            })
    }, [])

    const filteredRooms = rooms.filter(room =>
        room.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        room.type.toLowerCase().includes(searchTerm.toLowerCase())
    )

    if (loading) {
        return (
            <div className="loading">
                <div className="loading__spinner"></div>
                <span className="loading__text">Chargement des salles...</span>
            </div>
        )
    }

    if (error) {
        return (
            <div className="error">
                <div className="error__icon">⚠️</div>
                <p className="error__message">{error}</p>
                <p className="error__message text-muted mt-lg">
                    Assurez-vous que le serveur backend est lancé.
                </p>
            </div>
        )
    }

    return (
        <>
            <div className="search-bar">
                <svg className="search-bar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                    type="text"
                    className="search-bar__input"
                    placeholder="Rechercher une salle..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            <div className="room-grid">
                {filteredRooms.map((room, index) => (
                    <RoomCard
                        key={room.id}
                        room={room}
                        style={{ animationDelay: `${index * 50}ms` }}
                    />
                ))}
            </div>

            {filteredRooms.length === 0 && searchTerm && (
                <div className="schedule__empty">
                    <div className="schedule__empty-icon">🔍</div>
                    <p>Aucune salle trouvée pour "{searchTerm}"</p>
                </div>
            )}
        </>
    )
}

export default RoomList
