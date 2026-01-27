function Header({ authStatus }) {
    return (
        <header className="header">
            <div className="header__content">
                <div>
                    <h1 className="header__title">Salles TP</h1>
                    <p className="header__subtitle">Télécom Paris - Palaiseau</p>
                </div>
                {authStatus && (
                    <div className="header__status">
                        <span className="header__status-dot"></span>
                        <span>Connecté</span>
                    </div>
                )}
            </div>
        </header>
    )
}

export default Header
