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


### 4. Erreurs
Erreur :
```bash
Erreur d'authentification: [WinError 193] %1 n’est pas une application Win32 valide
your_IP_address - - [28/Jan/2026 11:36:41] "POST /api/auth/login HTTP/1.1" 401 -
```

Solution : 
Use Chrome's built-in driver support (Recommended)
Update headless_auth.py to handle Windows Chromedriver more reliably:
```bash
# Change this section in the authenticate function:
else:
    # Local development (use webdriver_manager)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
```

To: 
```bash
else:
    # Local development (use webdriver_manager)
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    except Exception as e:
        # Fallback: Try to use system Chrome without specifying chromedriver
        print(f"Webdriver manager failed: {e}, trying system Chrome...")
        driver = webdriver.Chrome(options=options)
```