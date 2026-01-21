from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import room_service

app = Flask(__name__)
CORS(app)

def get_default_dates():
    """Get default date range (today to 2 weeks from now)."""
    today = datetime.now()
    end = today + timedelta(days=14)
    return today.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get list of all available rooms."""
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
    """Get schedule for a specific room."""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        start_date, end_date = get_default_dates()
    
    try:
        result = room_service.fetch_schedule(room_id, start_date, end_date)
        if "error" in result:
            return jsonify({
                "success": False,
                "room_id": room_id,
                **result
            }), 401 if "authentication" in result.get("error", "").lower() else 500
        
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

@app.route('/api/schedule', methods=['GET'])
def get_all_schedules():
    """Get schedule for all rooms."""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        start_date, end_date = get_default_dates()
    
    try:
        rooms = room_service.get_unique_rooms()
        all_schedules = []
        
        for room in rooms:
            result = room_service.fetch_schedule(room['id'], start_date, end_date)
            all_schedules.append({
                "room": room,
                "schedule": result
            })
        
        return jsonify({
            "success": True,
            "start_date": start_date,
            "end_date": end_date,
            "schedules": all_schedules
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check if authentication cookies are available."""
    has_cookies = room_service.check_auth_status()
    return jsonify({
        "authenticated": has_cookies,
        "message": "Cookies disponibles" if has_cookies else "Authentification requise"
    })

@app.route('/api/auth/refresh', methods=['POST'])
def auth_refresh():
    try:
        success = room_service.refresh_auth()
        if success:
            return jsonify({
                "success": True,
                "message": "Authentification réussie, cookies sauvegardés"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Échec de l'authentification"
            }), 401
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
