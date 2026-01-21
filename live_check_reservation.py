import sys
import time
import json
import re
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import keyring

SERVICE_ID = "RIO_PROJECT_SYNAPSES"

END_DATE = "2025-12-22"
START_DATE = "2026-01-19"

URL = "https://synapses.telecom-paris.fr/salles/events-fc-scheduler"

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://synapses.telecom-paris.fr",
    "Referer": "https://synapses.telecom-paris.fr/salles/planning-multi",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

def load_rooms(file_path):
    rooms_map = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(content):
                content = content.strip()
                if not content:
                    break
                try:
                    obj, idx = decoder.raw_decode(content[pos:])
                    pos += idx
                    if 'id' in obj and 'nom' in obj:
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
                    while pos < len(content) and content[pos].isspace():
                        pos += 1
                except json.JSONDecodeError:
                    break
    except Exception as e:
        print(f"Error reading rooms file: {e}")
        return {}
    return rooms_map

def save_cookies_securely(cookies):
    try:
        if 'TPTauth' in cookies:
            keyring.set_password(SERVICE_ID, "TPTauth", cookies['TPTauth'])
        if 'SYNAPSES_SESSION' in cookies:
            keyring.set_password(SERVICE_ID, "SYNAPSES_SESSION", cookies['SYNAPSES_SESSION'])
        print(f"Cookies saved securely in keyring under service '{SERVICE_ID}'")
    except Exception as e:
        print(f"Error saving cookies to keyring: {e}")

def load_cookies_securely():
    try:
        tpt_auth = keyring.get_password(SERVICE_ID, "TPTauth")
        synapses_session = keyring.get_password(SERVICE_ID, "SYNAPSES_SESSION")
        
        if tpt_auth and synapses_session:
            return {
                "TPTauth": tpt_auth,
                "SYNAPSES_SESSION": synapses_session
            }
        return None
    except Exception as e:
        print(f"Error loading cookies from keyring: {e}")
        return None

def get_auth_cookies():
    
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    target_url = "https://synapses.telecom-paris.fr/salles/planning-multi"
    driver.get(target_url)
    
    cookies_dict = {}
    
    try:
        while True:
            current_cookies = driver.get_cookies()
            tpt_auth = next((c for c in current_cookies if c['name'] == 'TPTauth'), None)
            synapses_session = next((c for c in current_cookies if c['name'] == 'SYNAPSES_SESSION'), None)
            
            if tpt_auth and synapses_session:
                cookies_dict['TPTauth'] = tpt_auth['value']
                cookies_dict['SYNAPSES_SESSION'] = synapses_session['value']
                break
            
            time.sleep(1)
            try:
                driver.title
            except:
                sys.exit(1)
    finally:
        driver.quit()
    return cookies_dict



def fetch_schedule(room_id, room_name, cookies):
    payload = [
        ("salle[]", room_id),
        ("start", START_DATE),
        ("end", END_DATE)
    ]

    try:
        response = requests.post(
            URL, data=payload, headers=HEADERS, cookies=cookies, timeout=15
        )
        response.raise_for_status()
        
        try:
            events = response.json()
        except requests.exceptions.JSONDecodeError:
            return False
        
        if not events:
            print("Pas de cours dans cette salle")
            return True

        events.sort(key=lambda x: x.get('start', ''))
        
        for event in events:
            start = event.get('start', 'N/A').replace('T', ' ')
            end = event.get('end', 'N/A').replace('T', ' ')
            title = event.get('title', 'No Title')
            description = event.get('description', '')
            print(f"[{start} - {end}] {title} ({description})")
        return True
            
    except Exception as e:
        print(f"Request failed: {e}")
        if 'response' in locals():
            print(f"Response content snippet: {response.text[:200]}")
        return False

def main():
    rooms_file = 'salles_etage4.txt'
    rooms_map = load_rooms(rooms_file)
    
    target_rooms = []
    
    search_term = None
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    
    if search_term:
        if search_term in rooms_map:
             target_rooms.append((search_term, rooms_map[search_term]))
        else:
            found = False
            for name, rid in rooms_map.items():
                if search_term.lower() in name.lower():
                    target_rooms.append((name, rid))
                    found = True
                    break 
            
            if not found:
                 print(f"Salle '{search_term}' non trouvée. Vérification de toutes les salles...")
                 unique_ids = set()
                 for name, rid in rooms_map.items():
                     if rid not in unique_ids:
                         target_rooms.append((name, rid))
                         unique_ids.add(rid)
    else:
        print("Aucune salle spécifiée. Vérification de toutes les salles...")
        unique_ids = set()
        for name, rid in rooms_map.items():
             if rid not in unique_ids:
                 target_rooms.append((name, rid))
                 unique_ids.add(rid)

    if not target_rooms:
        print("Aucune salle à vérifier (fichier vide ou structure incorrecte).")
        return

    target_rooms.sort(key=lambda x: x[0])

    cookies = load_cookies_securely()
    if not cookies:
        print("Cookies absents, authentification requise...")
        cookies = get_auth_cookies()
        save_cookies_securely(cookies)

    refreshed_this_run = False

    for name, rid in target_rooms:
        success = fetch_schedule(rid, name, cookies)
        
        if not success:
            if not refreshed_this_run:
                print("Échec récupération. Tentative de rafraîchissement des cookies...")
                cookies = get_auth_cookies()
                save_cookies_securely(cookies)
                refreshed_this_run = True
                
                success = fetch_schedule(rid, name, cookies)
                if not success:
                    print(f"Abandon pour {name} après ré-authentification.")
            else:
                print(f"Échec pour {name} malgré cookies frais (erreur serveur ou autre).")

if __name__ == "__main__":
    main()
