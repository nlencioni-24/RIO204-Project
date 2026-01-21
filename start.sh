#!/bin/bash
cleanup() {
    echo "Arrêt des services..."
    kill 0
}

trap cleanup EXIT

PROJECT_ROOT=$(pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
APP_DIR="$PROJECT_ROOT/app"

# Lancement du Backend
if [ -d "$BACKEND_DIR" ]; then
    echo "📦 Démarrage du Backend (API)..."
    cd "$BACKEND_DIR"
    
    pip install -r requirements.txt
    
    nohup python3 api.py &
    BACKEND_PID=$!
    echo "✅ Backend lancé (PID: $BACKEND_PID)"
else
    echo "❌ Erreur : Dossier backend introuvable !"
    exit 1
fi

# Retour à la racine
cd "$PROJECT_ROOT"

# Lancement du Frontend
if [ -d "$APP_DIR" ]; then
    echo "🎨 Démarrage du Frontend..."
    cd "$APP_DIR"
    nohup python3 -m http.server 8000 &
    FRONTEND_PID=$!
    echo "✅ Frontend lancé (PID: $FRONTEND_PID)"
else
    echo "❌ Erreur : Dossier app introuvable !"
    exit 1
fi

echo "------------------------------------------------"
echo "🎉 Application RIO en cours d'exécution !"
echo "👉 Frontend : http://localhost:8000"
echo "👉 API Swagger : http://localhost:5001/apidocs"
echo "------------------------------------------------"
echo "Appuyez sur Ctrl+C pour arrêter."

wait
