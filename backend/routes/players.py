from flask import Blueprint, jsonify, request
from services.database import PokemonDatabase

players_bp = Blueprint('players', __name__, url_prefix='/api/players')

# Initialize database instance
db = PokemonDatabase()


@players_bp.route("", methods=["POST"])
def create_player():
    """Create a new player"""
    try:
        data = request.get_json()
        name = data.get("name")
        
        if not name:
            return jsonify({"error": "name is required"}), 400
        
        if not name.strip():
            return jsonify({"error": "name cannot be empty"}), 400
        
        # Check if player with this name already exists
        existing_player = db.get_player_by_name(name.strip())
        if existing_player:
            return jsonify({"error": "Player with this name already exists"}), 400
        
        # Check player limit (max 3 players allowed)
        all_players = db.get_all_players()
        if len(all_players) >= 3:
            return jsonify({"error": "Player limit reached"}), 400
        
        # Create new player
        player_id = db.create_player(name.strip())
        player = db.get_player_by_id(player_id)
        
        return jsonify({
            "message": "Player created successfully",
            "player": player
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create player: {str(e)}"}), 500


@players_bp.route("", methods=["GET"])
def get_all_players():
    """Get all players"""
    try:
        players = db.get_all_players()
        return jsonify({"players": players, "count": len(players)})

    except Exception as e:
        return jsonify({"error": f"Failed to get players: {str(e)}"}), 500


@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id):
    """Get a specific player by ID"""
    try:
        player = db.get_player_by_id(player_id)
        if player:
            return jsonify(player)
        else:
            return jsonify({"error": "Player not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to get player: {str(e)}"}), 500


@players_bp.route("/<int:player_id>/wins", methods=["GET"])
def get_player_wins(player_id):
    """Get all Pokemon wins for a specific player"""
    try:
        # Check if player exists
        player = db.get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        
        wins = db.get_player_pokemon_wins(player_id)
        win_count = db.get_pokemon_win_count(player_id)
        
        return jsonify({
            "player": player,
            "wins": wins,
            "total_pokemon_beaten": win_count
        })

    except Exception as e:
        return jsonify({"error": f"Failed to get player wins: {str(e)}"}), 500


@players_bp.route("/<int:player_id>/sessions", methods=["GET"])
def get_player_sessions(player_id):
    """Get all game sessions for a specific player"""
    try:
        # Check if player exists
        player = db.get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        
        limit = request.args.get("limit", 10, type=int)
        sessions = db.get_player_sessions(player_id, limit)
        
        return jsonify({
            "player": player,
            "sessions": sessions,
            "count": len(sessions)
        })

    except Exception as e:
        return jsonify({"error": f"Failed to get player sessions: {str(e)}"}), 500 