"""
API Flask pour le projet Synapses Room Scheduler.
Fournit les endpoints pour gérer les salles, les plannings et l'authentification.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import room_service
import headless_auth

app = Flask(__name__)
CORS(app)


def get_default_dates():
    """Retourne la plage de dates par défaut (aujourd'hui + 2 semaines)."""
    today = datetime.now()
    end = today + timedelta(days=14)
    return today.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# =============================================================================
# Endpoints Salles
# =============================================================================

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Retourne la liste de toutes les salles disponibles."""
    try:
        rooms = room_service.get_unique_rooms()
        return jsonify({
            "success": True,
            "rooms": rooms,
            "count": len(rooms)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "rooms": []
        }), 500


@app.route('/api/schedule/<int:room_id>', methods=['GET'])
def get_room_schedule(room_id):
    """Retourne le planning d'une salle spécifique."""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        start_date, end_date = get_default_dates()
    
    try:
        result = room_service.fetch_schedule(room_id, start_date, end_date)
        
        if "error" in result:
            status_code = 401 if "authentification" in result.get("error", "").lower() else 500
            return jsonify({
                "success": False,
                "room_id": room_id,
                **result
            }), status_code
        
        return jsonify({
            "success": True,
            "room_id": room_id,
            "start_date": start_date,
            "end_date": end_date,
            **result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "events": []
        }), 500


# =============================================================================
# Endpoints Authentification
# =============================================================================

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Vérifie si l'utilisateur est authentifié."""
    has_cookies = room_service.check_auth_status()
    return jsonify({
        "authenticated": has_cookies,
        "message": "Cookies disponibles" if has_cookies else "Authentification requise"
    })


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Authentifie l'utilisateur avec ses identifiants."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            "success": False, 
            "message": "Identifiant et mot de passe requis"
        }), 400
        
    try:
        cookies = headless_auth.authenticate(username, password)
        if cookies:
            room_service.save_cookies(cookies)
            return jsonify({
                "success": True, 
                "message": "Connexion réussie"
            })
        else:
            return jsonify({
                "success": False, 
                "message": "Identifiants invalides"
            }), 401
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Déconnecte l'utilisateur en supprimant les cookies."""
    room_service.delete_cookies()
    return jsonify({
        "success": True,
        "message": "Déconnexion réussie"
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de vérification de santé de l'API."""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
