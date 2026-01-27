import { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'

function ScheduleView() {
    const { roomId } = useParams()
    const navigate = useNavigate()
    const location = useLocation()
    const room = location.state?.room

    const [events, setEvents] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!roomId) return

        fetch(`/api/schedule/${roomId}`)
            .then(res => {
                if (!res.ok) throw new Error('Erreur serveur')
                return res.json()
            })
            .then(data => {
                if (data.success) {
                    setEvents(data.events || [])
                } else {
                    throw new Error(data.error || 'Erreur inconnue')
                }
                setLoading(false)
            })
            .catch(err => {
                setError(err.message)
                setLoading(false)
            })
    }, [roomId])

    const formatTime = (dateString) => {
        if (!dateString) return '--:--'
        const date = new Date(dateString)
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    }

    const formatDate = (dateString) => {
        if (!dateString) return ''
        const date = new Date(dateString)
        return date.toLocaleDateString('fr-FR', {
            weekday: 'long',
            day: 'numeric',
            month: 'long'
        })
    }

    const groupEventsByDate = (events) => {
        const grouped = {}
        events.forEach(event => {
            const dateKey = event.start ? event.start.split('T')[0] : 'unknown'
            if (!grouped[dateKey]) {
                grouped[dateKey] = []
            }
            grouped[dateKey].push(event)
        })
        return grouped
    }

    const getRoomName = () => {
        if (room) return room.nom
        return `Salle ${roomId}`
    }

    if (loading) {
        return (
            <div className="loading">
                <div className="loading__spinner"></div>
                <span className="loading__text">Chargement du planning...</span>
            </div>
        )
    }

    const groupedEvents = groupEventsByDate(events)

    return (
        <div className="schedule">
            <div className="schedule__header">
                <button className="schedule__back" onClick={() => navigate('/')}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="15 18 9 12 15 6" />
                    </svg>
                </button>
                <h2 className="schedule__title">{getRoomName()}</h2>
            </div>

            {error && (
                <div className="error mb-md">
                    <div className="error__icon">⚠️</div>
                    <p className="error__message">{error}</p>
                </div>
            )}

            {events.length === 0 && !error ? (
                <div className="schedule__empty">
                    <div className="schedule__empty-icon">📅</div>
                    <p>Aucune réservation prévue</p>
                    <p className="text-muted" style={{ marginTop: '8px', fontSize: '0.875rem' }}>
                        Cette salle est libre pour les prochains jours
                    </p>
                </div>
            ) : (
                <div className="schedule__events">
                    {Object.entries(groupedEvents).map(([date, dayEvents]) => (
                        <div key={date} className="fade-in">
                            <h3 style={{
                                fontSize: '0.875rem',
                                color: 'var(--color-text-secondary)',
                                marginBottom: '12px',
                                marginTop: '16px',
                                textTransform: 'capitalize'
                            }}>
                                {formatDate(dayEvents[0]?.start)}
                            </h3>
                            {dayEvents.map((event, index) => (
                                <div key={index} className="event-card">
                                    <div className="event-card__time">
                                        <span className="event-card__time-start">{formatTime(event.start)}</span>
                                        <span className="event-card__time-end">{formatTime(event.end)}</span>
                                    </div>
                                    <div className="event-card__content">
                                        <h4 className="event-card__title">{event.title}</h4>
                                        {event.description && (
                                            <p className="event-card__description">{event.description}</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default ScheduleView
