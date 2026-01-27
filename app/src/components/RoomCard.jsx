import { useNavigate } from 'react-router-dom'

function RoomCard({ room }) {
    const navigate = useNavigate()

    const getTypeClass = (type) => {
        const lower = type.toLowerCase()
        if (lower.includes('réunion')) return 'room-card__type--reunion'
        if (lower.includes('cours')) return 'room-card__type--cours'
        if (lower.includes('tp')) return 'room-card__type--tp'
        if (lower.includes('visio')) return 'room-card__type--visio'
        return ''
    }

    const getShortName = (nom) => {
        const match = nom.match(/^([A-Z0-9]+)/)
        return match ? match[1] : nom.split(' ')[0]
    }

    const getShortType = (type) => {
        if (type.includes('réunion')) return 'Réunion'
        if (type.includes('cours')) return 'Cours'
        if (type.includes('TP')) return 'TP'
        if (type.includes('Visio')) return 'Visio'
        return type
    }

    return (
        <div
            className="room-card fade-in"
            onClick={() => navigate(`/room/${room.id}`, { state: { room } })}
        >
            <div className="room-card__header">
                <span className="room-card__name">{getShortName(room.nom)}</span>
                <span className={`room-card__type ${getTypeClass(room.type)}`}>
                    {getShortType(room.type)}
                </span>
            </div>

            <div className="room-card__details">
                <div className="room-card__detail">
                    <svg className="room-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    <span>{room.capacite} places</span>
                </div>
                {room.accessibilite && (
                    <div className="room-card__detail">
                        <svg className="room-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="4" r="2" />
                            <path d="M12 6v6m0 0l-3 6m3-6l3 6" />
                        </svg>
                        <span>PMR</span>
                    </div>
                )}
            </div>
        </div>
    )
}

export default RoomCard
