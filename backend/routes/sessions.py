from flask import Blueprint, jsonify, request
from services.database import PokemonDatabase
from datetime import datetime
import json

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

# Initialize database instance
db = PokemonDatabase()


@sessions_bp.route("", methods=["POST"])
def create_game_session():
    """Create a new game session"""
    try:
        data = request.get_json()
        player_id = data.get("player_id")
        session_type = data.get("session_type")
        
        # Validate required fields
        if not player_id:
            return jsonify({"error": "player_id is required"}), 400
        
        if not session_type:
            return jsonify({"error": "session_type is required"}), 400
        
        # Validate session_type
        valid_session_types = ['random', 'specific_pokemon', 'batch', 'custom']
        if session_type not in valid_session_types:
            return jsonify({"error": f"session_type must be one of: {', '.join(valid_session_types)}"}), 400
        
        # Check if player exists
        player = db.get_player_by_id(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        
        # Validate difficulty if provided
        difficulty = data.get("difficulty")
        if difficulty:
            valid_difficulties = ['easy', 'medium', 'hard', 'mixed']
            if difficulty not in valid_difficulties:
                return jsonify({"error": f"difficulty must be one of: {', '.join(valid_difficulties)}"}), 400
        
        # Prepare session data
        session_data = {
            'player_id': player_id,
            'session_type': session_type,
            'difficulty': difficulty,
            'metadata': data.get('metadata', {}),
            'is_perfect_score': data.get('is_perfect_score', 0)
        }
        
        # Create the session
        session_id = db.create_game_session(session_data)
        
        # Get the created session
        created_session = db.get_game_session_by_id(session_id)
        
        return jsonify({
            "message": "Game session created successfully",
            "session": created_session
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create game session: {str(e)}"}), 500


@sessions_bp.route("/<int:session_id>", methods=["GET"])
def get_game_session(session_id):
    """Get a specific game session by ID"""
    try:
        session = db.get_game_session_by_id(session_id)
        if session:
            return jsonify(session)
        else:
            return jsonify({"error": "Game session not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to get game session: {str(e)}"}), 500


@sessions_bp.route("/<int:session_id>", methods=["PUT"])
def update_game_session(session_id):
    """Update a game session (typically used to end session and record results)"""
    try:
        data = request.get_json()
        
        # Check if session exists
        session = db.get_game_session_by_id(session_id)
        if not session:
            return jsonify({"error": "Game session not found"}), 404
        
        # Prepare updates
        updates = {}
        
        # Handle end_time
        if data.get("end_time"):
            updates["end_time"] = data["end_time"]
        elif data.get("end_session"):
            # Auto-set end_time to current timestamp
            updates["end_time"] = datetime.now().isoformat()
        
        # Handle scoring fields
        if "total_questions" in data:
            updates["total_questions"] = data["total_questions"]
        if "correct_answers" in data:
            updates["correct_answers"] = data["correct_answers"]
        if "score" in data:
            updates["score"] = data["score"]
        
        # Handle perfect score calculation
        if "total_questions" in data and "correct_answers" in data:
            is_perfect = data["correct_answers"] == data["total_questions"] and data["total_questions"] > 0
            updates["is_perfect_score"] = 1 if is_perfect else 0
        elif "is_perfect_score" in data:
            updates["is_perfect_score"] = 1 if data["is_perfect_score"] else 0
        
        # Handle metadata updates
        if "metadata" in data:
            updates["metadata"] = data["metadata"]
        
        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Update the session
        success = db.update_game_session(session_id, updates)
        if not success:
            return jsonify({"error": "Failed to update session"}), 500
        
        # If it's a perfect score, record Pokemon win
        if updates.get("is_perfect_score") == 1:
            # Check if this was a single-pokemon session
            metadata = session.get('metadata', {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            
            pokemon_id = metadata.get('pokemon_id')
            if pokemon_id and updates.get("total_questions", 0) > 0:
                db.record_pokemon_win(
                    session['player_id'],
                    pokemon_id,
                    session_id,
                    session.get('difficulty', 'medium'),
                    updates.get("total_questions", 0)
                )
        
        # Get updated session
        updated_session = db.get_game_session_by_id(session_id)
        
        return jsonify({
            "message": "Game session updated successfully",
            "session": updated_session
        })

    except Exception as e:
        return jsonify({"error": f"Failed to update game session: {str(e)}"}), 500 