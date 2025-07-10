from flask import Blueprint, jsonify, request
from services.database import PokemonDatabase
from datetime import datetime
import json

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

# Initialize database instance
db = PokemonDatabase()


@sessions_bp.route("", methods=["POST"])
def create_game_session():
    """Create a new game session
    ---
    tags:
      - sessions
    summary: Create a new game session
    description: Start a new trivia game session for a player with specified configuration
    parameters:
      - name: body
        in: body
        required: true
        description: Game session creation data
        schema:
          type: object
          required:
            - player_id
            - session_type
          properties:
            player_id:
              type: integer
              description: ID of the player starting the session
              example: 1
            session_type:
              type: string
              description: Type of trivia session
              enum: ["random", "specific_pokemon", "batch", "custom"]
              example: "specific_pokemon"
            difficulty:
              type: string
              description: Difficulty level for the session
              enum: ["easy", "medium", "hard", "mixed"]
              example: "medium"
            metadata:
              type: object
              description: Additional session configuration data
              example: {"pokemon_id": 25, "question_count": 5}
            is_perfect_score:
              type: integer
              description: Whether session requires perfect score (1 or 0)
              example: 0
    responses:
      201:
        description: Game session created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Game session created successfully"
            session:
              type: object
              properties:
                id:
                  type: integer
                  description: Session ID
                  example: 15
                player_id:
                  type: integer
                  description: Player ID
                  example: 1
                session_type:
                  type: string
                  description: Type of trivia session
                  example: "specific_pokemon"
                difficulty:
                  type: string
                  description: Difficulty level
                  example: "medium"
                start_time:
                  type: string
                  format: date-time
                  description: Session start time
                  example: "2024-01-15T14:00:00"
                end_time:
                  type: string
                  format: date-time
                  description: Session end time (null when active)
                  example: null
                metadata:
                  type: object
                  description: Session configuration data
                  example: {"pokemon_id": 25}
                total_questions:
                  type: integer
                  description: Total questions in session
                  example: 0
                correct_answers:
                  type: integer
                  description: Number of correct answers
                  example: 0
                score:
                  type: number
                  format: float
                  description: Final score percentage
                  example: 0.0
                is_perfect_score:
                  type: integer
                  description: Whether session had perfect score
                  example: 0
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              examples:
                missing_player: "player_id is required"
                missing_type: "session_type is required"
                invalid_type: "session_type must be one of: random, specific_pokemon, batch, custom"
                invalid_difficulty: "difficulty must be one of: easy, medium, hard, mixed"
      404:
        description: Player not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Player not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to create game session: Database error"
    """
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
    """Get a specific game session by ID
    ---
    tags:
      - sessions
    summary: Get game session by ID
    description: Retrieve detailed information for a specific game session
    parameters:
      - name: session_id
        in: path
        type: integer
        required: true
        description: The ID of the game session to retrieve
        example: 15
    responses:
      200:
        description: Game session successfully retrieved
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Session ID
              example: 15
            player_id:
              type: integer
              description: Player ID
              example: 1
            session_type:
              type: string
              description: Type of trivia session
              example: "specific_pokemon"
            difficulty:
              type: string
              description: Difficulty level
              example: "medium"
            start_time:
              type: string
              format: date-time
              description: Session start time
              example: "2024-01-15T14:00:00"
            end_time:
              type: string
              format: date-time
              description: Session end time (null if active)
              example: "2024-01-15T14:30:00"
            metadata:
              type: object
              description: Session configuration data
              example: {"pokemon_id": 25}
            total_questions:
              type: integer
              description: Total questions in session
              example: 5
            correct_answers:
              type: integer
              description: Number of correct answers
              example: 4
            score:
              type: number
              format: float
              description: Final score percentage
              example: 80.0
            is_perfect_score:
              type: integer
              description: Whether session had perfect score (1 or 0)
              example: 0
      404:
        description: Game session not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Game session not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to get game session: Database error"
    """
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
    """Update a game session (typically used to end session and record results)
    ---
    tags:
      - sessions
    summary: Update game session
    description: Update game session with results, end time, and scoring information
    parameters:
      - name: session_id
        in: path
        type: integer
        required: true
        description: The ID of the game session to update
        example: 15
      - name: body
        in: body
        required: true
        description: Session update data
        schema:
          type: object
          properties:
            end_time:
              type: string
              format: date-time
              description: Session end time (optional if end_session is used)
              example: "2024-01-15T14:30:00"
            end_session:
              type: boolean
              description: Auto-set end time to current timestamp
              example: true
            total_questions:
              type: integer
              description: Total questions answered in session
              example: 5
            correct_answers:
              type: integer
              description: Number of correct answers
              example: 4
            score:
              type: number
              format: float
              description: Final score percentage
              example: 80.0
            is_perfect_score:
              type: boolean
              description: Whether session achieved perfect score
              example: false
            metadata:
              type: object
              description: Updated session metadata
              example: {"completed": true, "final_pokemon": 25}
    responses:
      200:
        description: Game session updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Game session updated successfully"
            session:
              type: object
              properties:
                id:
                  type: integer
                  description: Session ID
                  example: 15
                player_id:
                  type: integer
                  description: Player ID
                  example: 1
                session_type:
                  type: string
                  description: Type of trivia session
                  example: "specific_pokemon"
                difficulty:
                  type: string
                  description: Difficulty level
                  example: "medium"
                start_time:
                  type: string
                  format: date-time
                  description: Session start time
                  example: "2024-01-15T14:00:00"
                end_time:
                  type: string
                  format: date-time
                  description: Session end time
                  example: "2024-01-15T14:30:00"
                total_questions:
                  type: integer
                  description: Total questions in session
                  example: 5
                correct_answers:
                  type: integer
                  description: Number of correct answers
                  example: 4
                score:
                  type: number
                  format: float
                  description: Final score percentage
                  example: 80.0
                is_perfect_score:
                  type: integer
                  description: Whether session had perfect score (1 or 0)
                  example: 0
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No valid fields to update"
      404:
        description: Game session not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Game session not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to update game session: Database error"
    """
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