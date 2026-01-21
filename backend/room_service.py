import json
import re
import requests
import keyring
import os

SERVICE_ID = "RIO_PROJECT_SYNAPSES2"
URL = "https://synapses.telecom-paris.fr/salles/events-fc-scheduler"

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://synapses.telecom-paris.fr",
    "Referer": "https://synapses.telecom-paris.fr/salles/planning-multi",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

def get_rooms_file_path():
    """Get the path to the rooms file relative to this module."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'salles_etage4.txt')

def load_rooms_raw():
    """Load raw room data from file, returning list of room objects."""
    file_path = get_rooms_file_path()
    rooms = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            decoder = json.JSONDecoder()
            idx = 0
            while idx < len(content):
                # Skip whitespace
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
                    # Move forward to try to find next valid JSON
                    idx += 1
    except Exception as e:
        print(f"Error reading rooms file: {e}")
        return []
    return rooms

def load_rooms_map():
    """Load rooms as a map of name -> id with multiple key variations."""
    rooms = load_rooms_raw()
    rooms_map = {}
    for obj in rooms:
        rooms_map[obj['nom']] = obj['id']
        match = re.search(r'([A-Z0-9]+)\s', obj['nom'])
        if match:
            rooms_map[match.group(1)] = obj['id']
        match_paren = re.search(r'\((.*?)\)', obj['nom'])
        if match_paren:
            rooms_map[match_paren.group(1)] = obj['id']
        parts = obj['nom'].split(' ')
        if parts:
            rooms_map[parts[0]] = obj['id']
    return rooms_map

def get_unique_rooms():
    """Get unique rooms (deduplicated by ID) for the frontend."""
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

def load_cookies_securely():
    """Load authentication cookies from keyring."""
    try:
        tpt_auth = keyring.get_password(SERVICE_ID, "TPTauth")
        ENT_SESSION = keyring.get_password(SERVICE_ID, "ENT-SESSION")
        
        if tpt_auth and ENT_SESSION:
            return {
                "TPTauth": tpt_auth,
                "ENT-SESSION": ENT_SESSION
            }
        return None
    except Exception as e:
        print(f"Error loading cookies from keyring: {e}")
        return None

def save_cookies_securely(cookies):
    """Save authentication cookies to keyring."""
    try:
        if 'TPTauth' in cookies:
            keyring.set_password(SERVICE_ID, "TPTauth", cookies['TPTauth'])
        if 'ENT-SESSION' in cookies:
            keyring.set_password(SERVICE_ID, "ENT-SESSION", cookies['ENT-SESSION'])
        print(f"Cookies saved securely in keyring under service '{SERVICE_ID}'")
        return True
    except Exception as e:
        print(f"Error saving cookies to keyring: {e}")
        return False

def get_auth_cookies():
    """Launch browser for authentication and retrieve cookies."""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    target_url = "https://synapses.telecom-paris.fr/salles/planning-multi"
    driver.get(target_url)
    
    cookies_dict = {}
    
    try:
        while True:
            current_cookies = driver.get_cookies()
            tpt_auth = next((c for c in current_cookies if c['name'] == 'TPTauth'), None)
            ENT_SESSION = next((c for c in current_cookies if c['name'] == 'ENT-SESSION'), None)
            
            if tpt_auth and ENT_SESSION:
                cookies_dict['TPTauth'] = tpt_auth['value']
                cookies_dict['ENT-SESSION'] = ENT_SESSION['value']
                break
            
            time.sleep(1)
            try:
                driver.title
            except:
                break
    finally:
        driver.quit()
    
    return cookies_dict

def check_auth_status():
    """Check if we have valid cookies stored."""
    cookies = load_cookies_securely()
    return cookies is not None

def refresh_auth():
    """Launch browser to get new authentication cookies."""
    cookies = get_auth_cookies()
    if cookies and 'TPTauth' in cookies and 'ENT-SESSION' in cookies:
        save_cookies_securely(cookies)
        return True
    return False

def fetch_schedule(room_id, start_date, end_date, cookies=None):
    """Fetch schedule for a room from Synapses API."""
    if cookies is None:
        cookies = load_cookies_securely()
    
    if not cookies:
        return {"error": "No authentication cookies available", "events": []}
    
    payload = [
        ("salle[]", room_id),
        ("start", start_date),
        ("end", end_date)
    ]

    try:
        response = requests.post(
            URL, data=payload, headers=HEADERS, cookies=cookies, timeout=15
        )
        response.raise_for_status()
        
        try:
            events = response.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": "Invalid response from server", "events": []}
        
        if not events:
            return {"events": [], "message": "Pas de cours dans cette salle"}

        events.sort(key=lambda x: x.get('start', ''))
        
        formatted_events = []
        for event in events:
            formatted_events.append({
                'start': event.get('start', ''),
                'end': event.get('end', ''),
                'title': event.get('title', 'No Title'),
                'description': event.get('description', '')
            })
        
        return {"events": formatted_events}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}", "events": []}
