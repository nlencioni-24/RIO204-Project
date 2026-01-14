import sys
import time
import json
import re
import requests
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

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

def save_cookies_to_file(cookies, file_path='cookies.json'):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
        print(f"Cookies saved to {file_path}")
    except Exception as e:
        print(f"Error saving cookies: {e}")

def load_cookies_from_file(file_path='cookies.json'):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cookies: {e}")
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

def parse_curl_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    url_match = re.search(r"curl\s+'([^']+)'", content)
    url = url_match.group(1) if url_match else None
    
    headers = {}
    header_matches = re.findall(r"-H\s+'([^:]+):\s*([^']+)'", content)
    for key, value in header_matches:
        if key.lower() not in ['cookie', 'content-length']:
            headers[key] = value

    data_match = re.search(r"--data-raw\s+'([^']+)'", content)
    data_str = data_match.group(1) if data_match else ""
    
    return url, headers, data_str

def fetch_schedule(room_id, room_name, cookies, template_file='room_schedule_infos.txt'):
    url, headers, data_template = parse_curl_template(template_file)
    
    if not url:
        print("Error: Pb URL")
        return False

    cookie_str = f"TPTauth={cookies['TPTauth']}; SYNAPSES_SESSION={cookies['SYNAPSES_SESSION']}"
    headers['Cookie'] = cookie_str
    
    parsed_data = urllib.parse.parse_qs(data_template)
    
    parsed_data['salle[]'] = [str(room_id)]
    
    new_body = urllib.parse.urlencode(parsed_data, doseq=True)
    
    try:
        response = requests.post(url, headers=headers, data=new_body)
        response.raise_for_status()
        
        events = response.json()
        
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
            print(f"Response content: {response.text}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python live_check_reservation.py <room_name>")
        return

    target_room_name = sys.argv[1]
    
    rooms_file = 'salles_etage4.txt'
    rooms_map = load_rooms(rooms_file)
    
    room_id = rooms_map.get(target_room_name)
    if not room_id:
        for name, rid in rooms_map.items():
            if target_room_name.lower() in name.lower():
                room_id = rid
                target_room_name = name
                break
    
    if not room_id:
        print(f"Salle '{target_room_name}' non trouvée dans {rooms_file}.")
        return

    cookies_file = 'cookies.json'
    cookies = load_cookies_from_file(cookies_file)
    
    success = False
    if cookies:
        success = fetch_schedule(room_id, target_room_name, cookies)
        if not success:
            print("Cookies invalides")
    
    if not success:
        print("Nouveau cookies...")
        cookies = get_auth_cookies()
        save_cookies_to_file(cookies, cookies_file)
        fetch_schedule(room_id, target_room_name, cookies)

if __name__ == "__main__":
    main()
