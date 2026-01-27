# 📚 Synapses Room Scheduler (Project RIO204)

> **Application de gestion et consultation des salles d'étude Télécom Paris.**  
> Interface moderne et synchronisation en temps réel avec le portail Synapses.

---

## 🚀 Fonctionnalités Clés

*   **⚡ Authentification Unique (SSO)** : Connexion automatique au portail Synapses via Selenium (Headless), avec gestion des redirections WAYF/Cerbere.
*   **📡 Données en Temps Réel** : Les statuts des salles ("Occupied", "Free") sont synchronisés directement avec les réservations officielles.
*   **📊 Dashboard Dynamique** : Vue d'ensemble de l'occupation des salles, avec indicateurs visuels (🔴 Occupé, 🟢 Libre, 🟠 Partiel).
*   **🌡️ Simulation IoT** : Intégration de faux capteurs (Température, Humidité, Présence) pour enrichir l'expérience utilisateur lorsque la salle est libre.
*   **📅 Emploi du Temps Détaillé** : Consultation des prochains cours pour chaque salle sur 7 jours.

---

## 📂 Architecture du Projet

Le projet repose sur une architecture simple et robuste :

*   **Backend (Python/Flask)** : Sert l'API REST et les fichiers statiques. Gère le scraping (Selenium) et la sécurité (Keyring).
*   **Frontend (Vanilla JS/HTML)** : Interface légère et rapide, sans framework lourd (pas de React/Vue), servie directement par Flask.

```
RIO204-Project/
├── backend/              # Cœur du serveur
│   ├── api.py            # Point d'entrée Flask & API REST
│   ├── headless_auth.py  # Bot d'authentification Selenium
│   └── room_service.py   # Gestion des données et cookies
├── frontend/             # Interface Utilisateur (Static)
│   ├── index.html        # Redirection
│   ├── login.html        # Page de connexion
│   ├── dashboard.html    # Tableau de bord principal
│   ├── room.html         # Détails d'une salle
│   └── src/              # Logic JS et Styles CSS
└── data/
    └── rooms.txt         # Configuration des salles surveillées
```

---

## 🛠️ Installation

### Prérequis
*   **Python 3.8+**
*   **Google Chrome** (nécessaire pour l'authentification automatique)

### 1. Cloner et préparer
```bash
git clone <url-du-repo>
cd RIO204-Project
```

### 2. Installer les dépendances Python
```bash
pip install -r requirements.txt
```
*(Le frontend n'a besoin d'aucune installation npm, tout est natif !)*

---

## ▶️ Utilisation

### 1. Lancer l'application
Démarrez simplement le serveur Python :

```bash
python backend/api.py
```
Le serveur démarrera sur **`http://localhost:5001`**.

### 2. Accéder à l'interface
Ouvrez votre navigateur sur `http://localhost:5001`.
*   Vous serez redirigé vers la page de **Login**.
*   Entrez vos identifiants **Télécom Paris** (IP Paris).
*   Une fois connecté, vous accédez au **Dashboard**.

---

## 🧩 Détails Techniques

### API Endpoints
*   `GET /api/rooms` : Liste des salles (Top 10 affichées).
*   `GET /api/schedule/<id>` : Récupère le planning (J+7) depuis Synapses.
*   `GET /api/user` : Infos de l'utilisateur connecté.
*   `POST /api/auth/login` : Lance le processus d'authentification Selenium.

### Logique de statut
La priorité d'affichage est la suivante :
1.  **Planning Synapses** : Si un cours est prévu *maintenant*, la salle est marquée **🔴 Occupied**.
2.  **Capteurs (Simulation)** : Si aucun cours, des données aléatoires simulent une occupation (partielle ou nulle).

---

*RIO204 - 2026*
