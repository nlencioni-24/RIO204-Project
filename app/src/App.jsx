import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from './components/Header'
import BottomNav from './components/BottomNav'
import RoomList from './components/RoomList'
import ScheduleView from './components/ScheduleView'
import LoginScreen from './components/LoginScreen'

function App() {
    const [authStatus, setAuthStatus] = useState(null) // null = loading, true = auth, false = not auth
    const [isCheckingAuth, setIsCheckingAuth] = useState(true)

    const checkAuthStatus = async () => {
        setIsCheckingAuth(true)
        try {
            const response = await fetch('/api/auth/status')
            const data = await response.json()
            setAuthStatus(data.authenticated)
        } catch (err) {
            // Si le backend n'est pas accessible, on considère non authentifié
            setAuthStatus(false)
        } finally {
            setIsCheckingAuth(false)
        }
    }

    useEffect(() => {
        checkAuthStatus()
    }, [])

    const handleLoginSuccess = () => {
        setAuthStatus(true)
    }

    // Écran de chargement initial
    if (isCheckingAuth) {
        return (
            <div className="splash-screen">
                <div className="splash-screen__content">
                    <div className="splash-screen__logo">
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
                    <h1 className="splash-screen__title">Salles TP</h1>
                    <div className="splash-screen__loader">
                        <div className="splash-screen__loader-bar"></div>
                    </div>
                    <p className="splash-screen__text">Vérification de la session...</p>
                </div>
            </div>
        )
    }

    // Si non authentifié, afficher l'écran de connexion
    if (!authStatus) {
        return <LoginScreen onLoginSuccess={handleLoginSuccess} />
    }

    // Application principale si authentifié
    return (
        <div className="app">
            <Header authStatus={authStatus} onAuthRefresh={setAuthStatus} />
            <main className="main">
                <Routes>
                    <Route path="/" element={<RoomList />} />
                    <Route path="/room/:roomId" element={<ScheduleView />} />
                </Routes>
            </main>
            <BottomNav />
        </div>
    )
}

export default App
