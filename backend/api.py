"""
API Flask pour le projet Synapses Room Scheduler.
Fournit les endpoints pour gérer les salles, les plannings et l'authentification.
"""
from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from datetime import datetime, timedelta
import room_service
import headless_auth
import headless_auth
import os
from models import db, UserReward, RoomStatus

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = 'super_secret_key_rio_project_2024'
CORS(app, supports_credentials=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/data/rewards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


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
    
    cookies = session.get('synapses_cookies')

    try:
        result = room_service.fetch_schedule(room_id, start_date, end_date, cookies)
        
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
    
    cookies = session.get('synapses_cookies')

    try:
        rooms = room_service.get_unique_rooms()
        all_schedules = []
        
        for room in rooms:
            try:
                result = room_service.fetch_schedule(room['id'], start_date, end_date, cookies)
                if "error" in result and "authentification" in result["error"].lower():
                    pass
                
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
    has_cookies = 'synapses_cookies' in session
    return jsonify({
        "authenticated": has_cookies,
        "message": "Session active" if has_cookies else "Authentification requise"
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    """Retourne les infos de l'utilisateur scrappées depuis Synapses."""
    cookies = session.get('synapses_cookies')
    try:
        info = room_service.get_user_info(cookies)
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
            session['synapses_cookies'] = cookies
            session.permanent = True # La session expire après 31 jours par défaut
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
    session.pop('synapses_cookies', None)
    return jsonify({
        "success": True,
        "message": "Déconnexion réussie"
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de vérification de santé de l'API."""
    return jsonify({"status": "ok"})



@app.route('/api/rewards', methods=['GET'])
def get_rewards():
    """Récupère les points de l'utilisateur connecté."""
    cookies = session.get('synapses_cookies')
    user_info = room_service.get_user_info(cookies)
    
    if not user_info or not user_info.get('name'):
         return jsonify({"success": False, "message": "User not identified"}), 401

    username = user_info['name']
    
    reward = UserReward.query.filter_by(username=username).first()
    points = reward.points if reward else 0
    
    return jsonify({
        "success": True, 
        "points": points,
        "username": username
    })

@app.route('/api/rewards/add', methods=['POST'])
def add_rewards():
    """Ajoute des points à l'utilisateur."""
    cookies = session.get('synapses_cookies')
    user_info = room_service.get_user_info(cookies)
    
    if not user_info or not user_info.get('name'):
        return jsonify({"success": False, "message": "User not identified"}), 401

    username = user_info['name']
    data = request.get_json()
    points_to_add = data.get('points', 0)
    
    #Sqlite pour pas de PostGres trop loud
    reward = UserReward.query.filter_by(username=username).first()
    if not reward:
        reward = UserReward(username=username, points=points_to_add)
        db.session.add(reward)
    else:
        reward.points += points_to_add
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "points": reward.points,
        "added": points_to_add
    })

@app.route('/api/rewards/leaderboard', methods=['GET'])
def get_leaderboard():
    """Retourne la liste de tous les utilisateurs et leurs scores."""
    rewards = UserReward.query.order_by(UserReward.points.desc()).all()
    return jsonify({
        "success": True,
        "leaderboard": [r.to_dict() for r in rewards]
    })


@app.route('/api/room/<int:room_id>/status', methods=['GET'])
def get_room_status(room_id):
    """Retourne l'état actuel (occupation) de la salle."""
    status = RoomStatus.query.get(room_id)
    occupancy = status.occupancy if status else 0
    return jsonify({
        "success": True,
        "room_id": room_id,
        "occupancy": occupancy
    })

@app.route('/api/rooms/status', methods=['GET'])
def get_all_rooms_status():
    """Retourne l'occupation de toutes les salles."""
    statuses = RoomStatus.query.all()
    status_map = {s.room_id: s.occupancy for s in statuses}
    return jsonify({
        "success": True,
        "statuses": status_map
    })

@app.route('/api/room/<int:room_id>/occupancy', methods=['POST'])
def update_room_occupancy(room_id):
    """Met à jour l'occupation de la salle."""
    data = request.get_json()
    action = data.get('action')
    value = data.get('value')
    
    status = RoomStatus.query.get(room_id)
    if not status:
        status = RoomStatus(room_id=room_id, occupancy=0)
        db.session.add(status)
    
    if action == 'enter':
        status.occupancy += 1
    elif action == 'leave':
        if status.occupancy > 0:
            status.occupancy -= 1
    elif action == 'set':
        if value is not None:
             status.occupancy = max(0, int(value))
             
    db.session.commit()
    
    return jsonify({
        "success": True,
        "room_id": room_id,
        "occupancy": status.occupancy
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

