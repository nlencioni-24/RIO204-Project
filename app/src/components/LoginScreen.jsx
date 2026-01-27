import { useState } from 'react'


function LoginScreen({ onLoginSuccess }) {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')

    const handleLogin = async (e) => {
        e.preventDefault()
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            })
            const data = await response.json()

            if (data.success) {
                onLoginSuccess && onLoginSuccess()
            } else {
                setError(data.message || 'Échec de la connexion')
            }
        } catch (err) {
            setError('Impossible de contacter le serveur. Vérifiez que le backend est lancé.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="login-screen">
            <div className="login-screen__container">
                {/* Logo / Icon */}
                <div className="login-screen__logo">
                    <div className="login-screen__logo-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16" />
                            <path d="M1 21h22" />
                            <path d="M9 6h1" />
                            <path d="M9 10h1" />
                            <path d="M9 14h1" />
                            <path d="M14 6h1" />
                            <path d="M14 10h1" />
                            <path d="M14 14h1" />
                            <rect x="9" y="17" width="6" height="4" />
                        </svg>
                    </div>
                </div>

                {/* Title */}
                <h1 className="login-screen__title">Salles TP</h1>
                <p className="login-screen__subtitle">Télécom Paris - Palaiseau</p>

                {/* Description */}
                <div className="login-screen__description">
                    <p>Consultez la disponibilité des salles de TP en temps réel.</p>
                    <p className="login-screen__hint">
                        Entrez vos identifiants Synapses pour accéder aux plannings.
                    </p>
                </div>

                {/* Error message */}
                {error && (
                    <div className="login-screen__error">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="12" y1="8" x2="12" y2="12" />
                            <line x1="12" y1="16" x2="12.01" y2="16" />
                        </svg>
                        <span>{error}</span>
                    </div>
                )}

                {/* Login Form */}
                <form onSubmit={handleLogin} className="login-screen__form">
                    <div className="login-screen__input-group">
                        <input
                            type="text"
                            placeholder="Identifiant (ex: prenom.nom)"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            className="login-screen__input"
                        />
                    </div>
                    <div className="login-screen__input-group">
                        <input
                            type="password"
                            placeholder="Mot de passe"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="login-screen__input"
                        />
                    </div>

                    <button
                        type="submit"
                        className={`login-screen__button ${isLoading ? 'login-screen__button--loading' : ''}`}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <>
                                <div className="login-screen__spinner"></div>
                                <span>Connexion...</span>
                            </>
                        ) : (
                            <>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                                    <polyline points="10 17 15 12 10 7" />
                                    <line x1="15" y1="12" x2="3" y2="12" />
                                </svg>
                                <span>Se connecter</span>
                            </>
                        )}
                    </button>
                </form>

                {/* Info */}
                <p className="login-screen__info">
                    Vos identifiants ne sont utilisés que pour récupérer le planning via Synapses.
                </p>
            </div>

            {/* Background decoration */}
            <div className="login-screen__bg-decoration"></div>
        </div>
    )
}

export default LoginScreen
