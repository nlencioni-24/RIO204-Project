"""
Service de gestion des salles et des réservations.
Gère le chargement des données, l'authentification et les appels API Synapses.
"""
import json
import re
import os
import requests
import keyring

# Configuration
SERVICE_ID = "RIO_PROJECT_SYNAPSES"
SYNAPSES_API_URL = "https://synapses.telecom-paris.fr/salles/events-fc-scheduler"

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://synapses.telecom-paris.fr",
    "Referer": "https://synapses.telecom-paris.fr/salles/planning-multi",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

def get_rooms_file_path():
    """Retourne le chemin vers le fichier de données des salles."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', 'rooms.txt')


def load_rooms_raw():
    """Charge les données brutes des salles depuis le fichier."""
    file_path = get_rooms_file_path()
    rooms = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            decoder = json.JSONDecoder()
            idx = 0
            while idx < len(content):
                while idx < len(content) and content[idx].isspace():
                    idx += 1
                if idx >= len(content):
                    break
                try:
                    obj, consumed = decoder.raw_decode(content, idx)
                    idx = consumed
                    if isinstance(obj, dict) and 'id' in obj and 'nom' in obj:
                        rooms.append(obj)
                except json.JSONDecodeError:
                    idx += 1
    except Exception as e:
        print(f"Erreur lecture fichier salles: {e}")
    return rooms


def get_unique_rooms():
    """Retourne la liste des salles uniques (dédupliquées par ID)."""
    rooms = load_rooms_raw()
    seen_ids = set()
    unique = []
    for room in rooms:
        if room['id'] not in seen_ids:
            unique.append({
                'id': room['id'],
                'nom': room['nom'],
                'type': room.get('type', 'Inconnu'),
                'capacite': room.get('capacite', 0),
                'accessibilite': room.get('accessibilite', False),
                'site': room.get('site', ''),
                'batiment': room.get('batiment', '')
            })
            seen_ids.add(room['id'])
    return unique

def load_cookies():
    """Charge les cookies d'authentification depuis le keyring."""
    try:
        cookies_json = keyring.get_password(SERVICE_ID, "COOKIES_JSON")
        if cookies_json:
            return json.loads(cookies_json)
        return None
    except Exception as e:
        print(f"Erreur chargement cookies: {e}")
        return None


def save_cookies(cookies):
    """Sauvegarde les cookies d'authentification dans le keyring."""
    try:
        keyring.set_password(SERVICE_ID, "COOKIES_JSON", json.dumps(cookies))
        return True
    except Exception as e:
        print(f"Erreur sauvegarde cookies: {e}")
        return False


def delete_cookies():
    """Supprime les cookies du keyring."""
    try:
        keyring.delete_password(SERVICE_ID, "COOKIES_JSON")
        return True
    except keyring.errors.PasswordDeleteError:
        return True  # Déjà supprimé
    except Exception as e:
        print(f"Erreur suppression cookies: {e}")
        return False


def check_auth_status():
    """Vérifie si des cookies valides sont stockés."""
    return load_cookies() is not None

def fetch_schedule(room_id, start_date, end_date):
    """Récupère le planning d'une salle depuis l'API Synapses."""
    cookies = load_cookies()
    
    if not cookies:
        return {"error": "Authentification requise", "events": []}
    
    payload = [
        ("salle[]", room_id),
        ("start", start_date),
        ("end", end_date)
    ]

    try:
        response = requests.post(
            SYNAPSES_API_URL, 
            data=payload, 
            headers=HEADERS, 
            cookies=cookies, 
            timeout=15
        )
        response.raise_for_status()
        
        try:
            events = response.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": "Réponse invalide du serveur", "events": []}
        
        if not events:
            return {"events": [], "message": "Pas de cours dans cette salle"}

        events.sort(key=lambda x: x.get('start', ''))
        
        formatted_events = []
        for event in events:
            formatted_events.append({
                'start': event.get('start', ''),
                'end': event.get('end', ''),
                'title': event.get('title', 'Sans titre'),
                'description': event.get('description', '')
            })
        
        return {"events": formatted_events}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur réseau: {str(e)}", "events": []}
    except Exception as e:
        return {"error": f"Erreur inattendue: {str(e)}", "events": []}

load_cookies_securely = load_cookies
save_cookies_securely = save_cookies
