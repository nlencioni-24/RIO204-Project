"""
Module d'authentification headless pour le portail Synapses.
Utilise Selenium pour gérer le SSO complexe de Télécom Paris.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def authenticate(username, password, headless=True):
    """
    Authentifie l'utilisateur sur le portail Synapses via Selenium.
    
    Args:
        username (str): Identifiant de l'utilisateur
        password (str): Mot de passe
        headless (bool): Si True, lance le navigateur en mode sans tête
    
    Returns:
        dict: Dictionnaire contenant les cookies {'TPTauth': ..., 'ENT-SESSION': ...}
        None: Si l'authentification échoue
    """
    driver = None
    try:
        # Configuration des options Chrome
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.implicitly_wait(10)
        
        # Navigation vers Synapses
        driver.get("https://synapses.telecom-paris.fr/salles/planning-multi")
        time.sleep(2)
        
        # Gestion du WAYF (Choix du fournisseur d'identité)
        if 'wayf' in driver.current_url.lower() or 'idp_select' in driver.page_source:
            try:
                # Sélection de Télécom Paris via JavaScript
                driver.execute_script("""
                    var select = document.getElementById('idp_select');
                    if (select) {
                        select.value = 'https://cerbere.telecom-paris.fr/saml2/idp';
                        var event = new Event('change', { bubbles: true });
                        select.dispatchEvent(event);
                    }
                """)
                time.sleep(0.5)
                
                # Validation du formulaire
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                driver.execute_script("arguments[0].click();", submit_btn)
                time.sleep(2)
            except Exception as e:
                print(f"Erreur WAYF: {e}")
        
        # Gestion du formulaire de connexion
        if 'login' in driver.current_url.lower() or 'identifiant' in driver.page_source.lower():
            try:
                time.sleep(1)
                username_field = driver.find_element(By.NAME, "identifiant")
                password_field = driver.find_element(By.NAME, "mdp")
                
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                driver.execute_script("arguments[0].click();", submit_btn)
                
            except Exception as e:
                print(f"Erreur Login: {e}")
                return None
        
        # Attente de la redirection vers Synapses
        max_wait = 30
        for i in range(max_wait):
            time.sleep(1)
            current_url = driver.current_url
            if 'synapses' in current_url and 'cerbere' not in current_url:
                break
        
        # Récupération des cookies
        cookies_list = driver.get_cookies()
        cookies = {}
        for c in cookies_list:
            if 'synapses' in c.get('domain', ''):
                cookies[c['name']] = c['value']
        
        # Vérification des cookies requis
        if 'TPTauth' in cookies and ('ENT-SESSION' in cookies or 'SYNAPSES_SESSION' in cookies):
            return cookies
        else:
            return None
            
    except Exception as e:
        print(f"Erreur d'authentification: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
