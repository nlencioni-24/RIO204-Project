# Synapses Room Scheduler - Projet RIO204

Application web permettant de consulter les plannings des salles de Télécom Paris via le portail Synapses. Ce projet inclut un backend Flask qui gère l'authentification et l'API, et un frontend React pour l'interface utilisateur.

## 🚀 Fonctionnalités

- Authentification automatique sur le portail Synapses (SSO Télécom Paris).
- Consultation des plannings de salles spécifiques.
- Interface moderne et responsive.
- Gestion sécurisée des sessions (cookies).

## 📂 Architecture

```
RIO204-Project/
├── app/                  # Frontend React (Vite)
│   ├── src/              # Code source frontend
│   │   ├── components/   # Composants React
│   │   └── ...
│   └── vite.config.js    # Configuration Vite (proxy API)
├── backend/              # Backend Flask
│   ├── api.py            # API REST (Endpoints)
│   ├── room_service.py   # Logique métier et gestion cookies
│   └── headless_auth.py  # Authentification Selenium
├── data/
│   └── rooms.txt         # Identifiants des salles (ID Synapses)
└── requirements.txt      # Dépendances Python
```

## 🛠️ Prérequis

- **Python 3.8+**
- **Node.js 16+**
- **Google Chrome** (installé sur la machine pour Selenium)

## 📦 Installation

### 1. Backend (Python)

```bash
# Installer les dépendances
pip install -r requirements.txt
```

### 2. Frontend (Node.js)

```bash
cd app
npm install
```

## ▶️ Lancement

### Lancer le Backend

Dans un terminal à la racine du projet :

```bash
cd backend
python api.py
```
Le backend démarrera sur `http://localhost:5001`.

### Lancer le Frontend

Dans un autre terminal :

```bash
cd app
npm run dev
```
L'application sera accessible sur `http://localhost:5173`.

---

## 🔐 Fonctionnement de l'Authentification

Le portail Synapses utilise un système **SSO (Single Sign-On)** complexe avec plusieurs redirections (WAYF -> Cerbere -> Synapses).

L'authentification est gérée par le module `backend/headless_auth.py` :

1. **Selenium** lance une instance de Chrome (en mode headless/invisible).
2. Il navigue vers Synapses et détecte la redirection vers le portail d'authentification (WAYF).
3. Il sélectionne automatiquement "Télécom Paris".
4. Il remplit le formulaire de connexion avec vos identifiants.
5. Il attend que toutes les redirections SAML soient terminées.
6. Il extrait les cookies de session (`TPTauth`, `ENT-SESSION`) et les renvoie au backend.
7. Le backend stocke ces cookies de manière sécurisée (via `keyring`) pour les utiliser lors des appels API ultérieurs via `requests`.

## 📡 API Endpoints

- `GET /api/rooms` : Liste toutes les salles surveillées.
- `GET /api/schedule/<room_id>` : Récupère le planning d'une salle.
- `POST /api/auth/login` : Connecte l'utilisateur.
- `GET /api/auth/status` : Vérifie l'état de la connexion.
- `POST /api/auth/logout` : Déconnecte l'utilisateur.

## 📝 Configuration des Salles

Pour ajouter ou modifier des salles, éditez le fichier `data/rooms.txt`. Le format est un objet JSON contenant l'ID et le nom de la salle.

Exemple :
```json
{"id": 1234, "nom": "C401 (Salle de TP)"}
```

---
*Projet RIO204 - 2026*
