from flask import Blueprint, jsonify, request
from services.database import PokemonDatabase

players_bp = Blueprint('players', __name__, url_prefix='/api/players')

# Initialize database instance
db = PokemonDatabase()


@players_bp.route("", methods=["POST"])
def create_player():
    """Create a new player
    ---
    tags:
      - players
    summary: Create a new player
    description: Register a new player for the Pokemon trivia game (max 3 players allowed)
    parameters:
      - name: body
        in: body
        required: true
        description: Player creation data
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Player name (must be unique)
              example: "Ash Ketchum"
              minLength: 1
    responses:
      201:
        description: Player created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Player created successfully"
            player:
              type: object
              properties:
                id:
                  type: integer
                  description: Player ID
                  example: 1
                name:
                  type: string
                  description: Player name
                  example: "Ash Ketchum"
                created_at:
                  type: string
                  format: date-time
                  description: Player creation timestamp
                  example: "2024-01-15T10:30:00"
                total_sessions:
                  type: integer
                  description: Total number of game sessions
                  example: 0
                perfect_scores:
                  type: integer
                  description: Number of perfect score sessions
                  example: 0
      400:
        description: Invalid input or player limit reached
        schema:
          type: object
          properties:
            error:
              type: string
              examples:
                missing_name: "name is required"
                empty_name: "name cannot be empty"
                duplicate_name: "Player with this name already exists"
                player_limit: "Player limit reached"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to create player: Database error"
    """
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
    """Get all players
    ---
    tags:
      - players
    summary: Get all players
    description: Retrieve a list of all registered players with their statistics
    responses:
      200:
        description: List of players successfully retrieved
        schema:
          type: object
          properties:
            players:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Player ID
                    example: 1
                  name:
                    type: string
                    description: Player name
                    example: "Ash Ketchum"
                  created_at:
                    type: string
                    format: date-time
                    description: Player creation timestamp
                    example: "2024-01-15T10:30:00"
                  total_sessions:
                    type: integer
                    description: Total number of game sessions
                    example: 5
                  perfect_scores:
                    type: integer
                    description: Number of perfect score sessions
                    example: 2
            count:
              type: integer
              description: Total number of players
              example: 2
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to get players: Database error"
    """
    try:
        players = db.get_all_players()
        return jsonify({"players": players, "count": len(players)})

    except Exception as e:
        return jsonify({"error": f"Failed to get players: {str(e)}"}), 500


@players_bp.route("/<int:player_id>", methods=["GET"])
def get_player(player_id):
    """Get a specific player by ID
    ---
    tags:
      - players
    summary: Get player by ID
    description: Retrieve detailed information for a specific player
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: The ID of the player to retrieve
        example: 1
    responses:
      200:
        description: Player details successfully retrieved
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Player ID
              example: 1
            name:
              type: string
              description: Player name
              example: "Ash Ketchum"
            created_at:
              type: string
              format: date-time
              description: Player creation timestamp
              example: "2024-01-15T10:30:00"
            total_sessions:
              type: integer
              description: Total number of game sessions
              example: 5
            perfect_scores:
              type: integer
              description: Number of perfect score sessions
              example: 2
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
              example: "Failed to get player: Database error"
    """
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
    """Get all Pokemon wins for a specific player
    ---
    tags:
      - players
    summary: Get player Pokemon wins
    description: Retrieve all Pokemon that the player has defeated with perfect scores
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: The ID of the player
        example: 1
    responses:
      200:
        description: Player wins successfully retrieved
        schema:
          type: object
          properties:
            player:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: "Ash Ketchum"
            wins:
              type: array
              items:
                type: object
                properties:
                  pokemon_id:
                    type: integer
                    description: ID of defeated Pokemon
                    example: 25
                  pokemon_name:
                    type: string
                    description: Name of defeated Pokemon
                    example: "pikachu"
                  session_id:
                    type: integer
                    description: Game session where Pokemon was defeated
                    example: 15
                  difficulty:
                    type: string
                    description: Difficulty level of the session
                    example: "medium"
                  questions_answered:
                    type: integer
                    description: Number of questions answered correctly
                    example: 5
                  defeated_at:
                    type: string
                    format: date-time
                    description: When the Pokemon was defeated
                    example: "2024-01-15T14:30:00"
            total_pokemon_beaten:
              type: integer
              description: Total number of unique Pokemon defeated
              example: 3
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
              example: "Failed to get player wins: Database error"
    """
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
    """Get all game sessions for a specific player
    ---
    tags:
      - players
    summary: Get player game sessions
    description: Retrieve all game sessions played by a specific player
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: The ID of the player
        example: 1
      - name: limit
        in: query
        type: integer
        description: Maximum number of sessions to return
        default: 10
        example: 10
    responses:
      200:
        description: Player sessions successfully retrieved
        schema:
          type: object
          properties:
            player:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: "Ash Ketchum"
            sessions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Session ID
                    example: 15
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
            count:
              type: integer
              description: Number of sessions returned
              example: 5
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
              example: "Failed to get player sessions: Database error"
    """
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