# Synapses Room Scheduler

Application Web permettant de consulter les emplois du temps des salles de Télécom Paris.

## Lancement Local

Pour lancer le projet directement sur votre machine :

### 1. Prérequis
*   **Python 3** installé.
*   **Google Chrome** installé sur votre ordinateur (nécessaire pour l'authentification).
    *   *Pas besoin d'installer Chromedriver manuellement, le script le fera tout seul.*

### Si vous n'avez pas Google Chrome (Linux)
Lancez ces commandes dans le terminal :
```bash
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver
```

### 2. Installation
Ouvrez un terminal à la racine du projet :

```bash
# Installer les librairies Python
pip install -r requirements.txt
```

### 3. Démarrage
```bash
# Lancer le serveur
python backend/api.py
```

L'application sera accessible sur : http://localhost:5001
