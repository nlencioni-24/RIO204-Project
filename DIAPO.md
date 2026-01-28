# Architecture de l'Application

Voici les schémas pour votre présentation.

### 1. Architecture Globale (Style "Carte")

```mermaid
graph LR
    %% Actors
    User((User))

    %% Application
    subgraph App["Our Application"]
        Frontend["Web Interface<br/>(Frontend)"]
        Backend["Python Server<br/>(Backend API)"]
        
        subgraph Features["Features"]
            DB[("Database<br/>(User Info & Rewards)")]
        end
    end

    %% External System
    Target["Synapses Portal<br/>(Télécom Paris)"]

    %% Data Flow
    User <-->| Web Navigation | Frontend
    Frontend <-->| REST API | Backend
    Backend <-->| Automated Connection | Target
    Backend <-->| Read/Write | DB

    %% Styles
    style User fill:#E3F2FD,stroke:#1E88E5,stroke-width:2px
    style Frontend fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style Backend fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px
    style Target fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style DB fill:#FFEBEE,stroke:#C62828,stroke-width:2px

    style App fill:#F5F7FA,stroke:#90A4AE,stroke-width:2px
    style Features fill:#FFFFFF,stroke:#90A4AE,stroke-width:1px,stroke-dasharray: 5 5
```

### 2. Flux Détaillé : Récupération d'un Planning

Ce diagramme de séquence détaille les appels réseaux et les routes API utilisées.

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Web Frontend
    participant Backend as Backend API (Python)
    participant Synapses as Synapses 

    User->>Frontend: 1. Selects "Room 4C101"

    %% Internal API Call
    Frontend->>Backend: 2. GET /api/schedule/4C101

    %% Backend Processing
    Note right of Backend: Verify user authentication

    %% External Request
    Backend->>Synapses: 3. POST /rooms/events-scheduler
    Note right of Synapses: Headers: {Auth-Info}<br/>Body: {room_id: 45}

    %% Responses
    Synapses-->>Backend: 4. 200 OK (Raw JSON data)
    Backend-->>Frontend: 5. 200 OK (Formatted JSON)

    Frontend-->>User: 6. Update calendar view
```

**Légende pour l'oral :**
*   **En vert** : Ce qui se passe dans le navigateur de l'utilisateur.
*   **En orange/central** : Votre serveur qui enrichit la requête avec les cookies de session.
*   **En violet/droite** : Le serveur de l'école qui reçoit une requête officielle.

### 3. Liste des Endpoints API

Voici les principales routes utiles pour le projet, présentées sous forme de tableau.

```mermaid
graph TB

    Backend["Backend API<br/>(Flask Server)"]

    %% Authentication Module
    subgraph Auth["Authentication Module"]
        direction TB
        Login["POST /api/auth/login<br/>Create user session"]
        Status["GET /api/auth/status<br/>Check authentication state"]
    end

    %% Data Module
    subgraph Data["Data Module"]
        direction TB
        Rooms["GET /api/rooms<br/>List available rooms"]
        Schedule["GET /api/schedule/{id}<br/>Retrieve room schedule"]
        User["GET /api/user<br/>Fetch user identity"]
    end

    %% Flow
    Backend --> Auth
    Backend --> Data

    Auth --> Login
    Auth --> Status

    Data --> Rooms
    Data --> Schedule
    Data --> User

    %% Styles

    %% Backend API (Orange)
    style Backend fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px

    %% Authentication Module (Green)
    style Auth fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style Login fill:#FFFFFF,stroke:#2E7D32
    style Status fill:#FFFFFF,stroke:#2E7D32

    %% Data Module (Blue)
    style Data fill:#E3F2FD,stroke:#1E88E5,stroke-width:2px
    style Rooms fill:#FFFFFF,stroke:#1E88E5
    style Schedule fill:#FFFFFF,stroke:#1E88E5
    style User fill:#FFFFFF,stroke:#1E88E5
```