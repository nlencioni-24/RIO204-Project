"""
API Flask pour le projet Synapses Room Scheduler.
Fournit les endpoints pour gérer les salles, les plannings et l'authentification.
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import room_service
import headless_auth
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)


def get_default_dates():
    """Retourne la plage de dates par défaut (aujourd'hui + 2 semaines)."""
    today = datetime.now()
    end = today + timedelta(days=14)
    return today.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


@app.route('/')
def serve_index():
    # Rediriger vers login si pas cookie? Non, le frontend s'en charge.
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


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

@app.route('/api/schedules', methods=['GET'])
def get_all_schedules():
    """
    Retourne le planning de toutes les salles.
    Peut être lent ! (itération sur toutes les salles)
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        # Par défaut, juste aujourd'hui pour être plus rapide
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    
    try:
        rooms = room_service.get_unique_rooms()
        all_schedules = []
        
        for room in rooms:
            try:
                result = room_service.fetch_schedule(room['id'], start_date, end_date)
                if "error" in result and "authentification" in result["error"].lower():
                    return jsonify({"success": False, "error": "Authentification requise"}), 401
                
                all_schedules.append({
                    "room": room,
                    "schedule": result
                })
            except Exception:
                continue
                
        return jsonify({
            "success": True,
            "schedules": all_schedules
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Vérifie si l'utilisateur est authentifié."""
    has_cookies = room_service.check_auth_status()
    user_info = None
    if has_cookies:
        pass
        
    return jsonify({
        "authenticated": has_cookies,
        "message": "Cookies disponibles" if has_cookies else "Authentification requise"
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    """Retourne les infos de l'utilisateur scrappées depuis Synapses."""
    try:
        info = room_service.get_user_info()
        if info:
            return jsonify({
                "success": True, 
                "user": info
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Impossible de récupérer les infos utilisateur"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500


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
