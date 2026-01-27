import { NavLink } from 'react-router-dom'

function BottomNav() {
    return (
        <nav className="bottom-nav">
            <ul className="bottom-nav__list">
                <li className="bottom-nav__item">
                    <NavLink
                        to="/"
                        className={({ isActive }) =>
                            `bottom-nav__link ${isActive ? 'bottom-nav__link--active' : ''}`
                        }
                    >
                        <svg className="bottom-nav__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16" />
                            <path d="M1 21h22" />
                            <path d="M9 6h1" />
                            <path d="M9 10h1" />
                            <path d="M14 6h1" />
                            <path d="M14 10h1" />
                        </svg>
                        <span className="bottom-nav__label">Salles</span>
                    </NavLink>
                </li>
            </ul>
        </nav>
    )
}

export default BottomNav
