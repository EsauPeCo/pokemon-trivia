from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from services.pokemon_fetcher import fetch_pokemon_data
from services.database import PokemonDatabase
from ai import TriviaGenerator
import os

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Initialize database
db = PokemonDatabase()

# Initialize AI trivia generator
trivia_generator = TriviaGenerator()


# Initialize Pokemon data if database is empty
def initialize_pokemon_data():
    if db.database_is_empty():
        print("Database is empty. Fetching Pokémon data from PokeAPI...")
        pokemons = fetch_pokemon_data()

        if pokemons:
            print(f"Loading {len(pokemons)} Pokémon into database...")
            for i, pokemon in enumerate(pokemons, 1):
                db.insert_pokemon(pokemon)
                if i % 10 == 0:
                    print(f"Loaded {i}/{len(pokemons)} Pokemon...")

            print(f"Successfully loaded {len(pokemons)} Pokémon into database!")
        else:
            print("Failed to fetch Pokemon data!")
    else:
        pokemon_count = db.get_pokemon_count()
        print(f"Database already contains {pokemon_count} Pokémon")


# Initialize data on startup
initialize_pokemon_data()


# Favicon routes
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "icons", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.route("/favicon-32x32.png")
def favicon_32():
    return send_from_directory("icons", "favicon-32x32.png", mimetype="image/png")


# Home route
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pokémon Trivia API</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    </head>
    <body>
        <h1>Pokémon Trivia API</h1>
        <p>Database contains {} Pokémon</p>
    </body>
    </html>
    """.format(
        db.get_pokemon_count()
    )


# Get all Pokémon - now using database
@app.route("/api/pokemon", methods=["GET"])
def get_pokemons():
    # Return only essential fields for the list view
    simplified_pokemons = db.get_pokemon_list()
    return jsonify(simplified_pokemons)


# Get one Pokémon by ID - now using database
@app.route("/api/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    pokemon = db.get_pokemon_by_id(pokemon_id)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({"error": "Pokémon not found"}), 404


# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "pokemon_count": db.get_pokemon_count(),
            "database": "connected",
        }
    )


# AI Trivia endpoints
@app.route("/api/trivia/generate", methods=["POST"])
def generate_trivia():
    """Generate a trivia question for a specific Pokemon"""
    try:
        data = request.get_json()
        pokemon_id = data.get("pokemon_id")
        question_type = data.get("question_type", "general")
        difficulty = data.get("difficulty", "medium")
        focus = data.get("focus")

        if not pokemon_id:
            return jsonify({"error": "pokemon_id is required"}), 400

        # Get Pokemon data from database
        pokemon_data = db.get_pokemon_by_id(pokemon_id)
        if not pokemon_data:
            return jsonify({"error": "Pokemon not found"}), 404

        # Generate trivia question
        question = trivia_generator.generate_question(
            pokemon_data,
            question_type=question_type,
            difficulty=difficulty,
            focus=focus,
        )

        # Store question in database
        question_data = {
            'pokemon_id': pokemon_id,
            'question': question.get('question'),
            'options': question.get('options', []),
            'correct_answer': question.get('correct_answer'),
            'question_type': question_type,
            'difficulty': difficulty,
            'focus': focus
        }
        
        question_id = db.insert_trivia_question(question_data)
        
        # Add question ID to response
        question['id'] = question_id

        return jsonify(question)

    except Exception as e:
        return jsonify({"error": f"Failed to generate trivia: {str(e)}"}), 500


@app.route("/api/trivia/random", methods=["GET"])
def generate_random_trivia():
    """Generate a random trivia question from a random Pokemon"""
    try:
        difficulty = request.args.get("difficulty")

        # Get random Pokemon
        pokemon_list = db.get_pokemon_list()
        if not pokemon_list:
            return jsonify({"error": "No Pokemon found in database"}), 404

        import random

        random_pokemon = random.choice(pokemon_list)

        # Get full Pokemon data
        pokemon_data = db.get_pokemon_by_id(random_pokemon["id"])

        # Generate random trivia question
        question = trivia_generator.generate_random_question(
            pokemon_data, difficulty=difficulty
        )

        # Store question in database
        question_data = {
            'pokemon_id': random_pokemon["id"],
            'question': question.get('question'),
            'options': question.get('options', []),
            'correct_answer': question.get('correct_answer'),
            'question_type': question.get('question_type', 'general'),
            'difficulty': question.get('difficulty', difficulty or 'medium'),
            'focus': question.get('focus')
        }
        
        question_id = db.insert_trivia_question(question_data)
        
        # Add question ID to response
        question['id'] = question_id

        return jsonify(question)

    except Exception as e:
        return jsonify({"error": f"Failed to generate random trivia: {str(e)}"}), 500


@app.route("/api/trivia/batch", methods=["POST"])
def generate_trivia_batch():
    """Generate multiple trivia questions"""
    try:
        data = request.get_json()
        count = data.get("count", 5)
        difficulty = data.get("difficulty")
        pokemon_ids = data.get("pokemon_ids", [])

        # Validate count
        if count > 20:
            return jsonify({"error": "Maximum 20 questions per batch"}), 400

        # Get Pokemon data
        if pokemon_ids:
            # Use specific Pokemon
            pokemon_list = []
            for pokemon_id in pokemon_ids:
                pokemon = db.get_pokemon_by_id(pokemon_id)
                if pokemon:
                    pokemon_list.append(pokemon)
        else:
            # Use random Pokemon
            all_pokemon = db.get_pokemon_list()
            import random

            pokemon_list = [
                db.get_pokemon_by_id(p["id"])
                for p in random.sample(all_pokemon, min(count, len(all_pokemon)))
            ]

        if not pokemon_list:
            return jsonify({"error": "No valid Pokemon found"}), 404

        # Generate multiple questions
        questions = trivia_generator.generate_multiple_questions(
            pokemon_list, count=count, difficulty=difficulty
        )

        # Store each question in database and add IDs
        for question in questions:
            question_data = {
                'pokemon_id': question.get('pokemon_id'),
                'question': question.get('question'),
                'options': question.get('options', []),
                'correct_answer': question.get('correct_answer'),
                'question_type': question.get('question_type', 'general'),
                'difficulty': question.get('difficulty', difficulty or 'medium'),
                'focus': question.get('focus')
            }
            
            question_id = db.insert_trivia_question(question_data)
            question['id'] = question_id

        return jsonify({"questions": questions, "count": len(questions)})

    except Exception as e:
        return jsonify({"error": f"Failed to generate trivia batch: {str(e)}"}), 500


# Question rating endpoints
@app.route("/api/trivia/questions/rating", methods=["POST"])
def update_questions_rating():
    """Update rating for multiple trivia questions"""
    try:
        data = request.get_json()
        updates = data.get("updates", [])
        
        if not updates:
            return jsonify({"error": "updates array is required"}), 400
        
        if not isinstance(updates, list):
            return jsonify({"error": "updates must be an array"}), 400
        
        if len(updates) > 50:  # Limit batch size
            return jsonify({"error": "Maximum 50 updates per batch"}), 400
        
        results = []
        errors = []
        
        for update in updates:
            question_id = update.get("question_id")
            action = update.get("action")
            
            # Validate each update
            if not question_id:
                errors.append({"error": "question_id is required", "update": update})
                continue
                
            if action not in ["like", "dislike"]:
                errors.append({"error": "action must be 'like' or 'dislike'", "update": update})
                continue
            
            try:
                # Update the rating
                success = db.update_question_rating(question_id, action)
                if success:
                    # Get updated question data
                    question = db.get_trivia_question_by_id(question_id)
                    if question:
                        results.append({
                            "question_id": question_id,
                            "action": action,
                            "success": True,
                            "likes": question['likes'],
                            "dislikes": question['dislikes']
                        })
                    else:
                        errors.append({
                            "error": "Question not found",
                            "question_id": question_id,
                            "action": action
                        })
                else:
                    errors.append({
                        "error": "Failed to update rating",
                        "question_id": question_id,
                        "action": action
                    })
                    
            except Exception as e:
                errors.append({
                    "error": f"Failed to update question {question_id}: {str(e)}",
                    "question_id": question_id,
                    "action": action
                })
        
        response = {
            "message": f"Processed {len(results)} successful updates",
            "results": results,
            "successful_count": len(results),
            "error_count": len(errors)
        }
        
        if errors:
            response["errors"] = errors
        
        # Return 207 Multi-Status if there were partial failures, otherwise 200
        status_code = 207 if errors and results else 200 if results else 400
        
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": f"Failed to update question ratings: {str(e)}"}), 500


# Question retrieval endpoints
@app.route("/api/trivia/questions/<int:question_id>", methods=["GET"])
def get_question(question_id):
    """Get a specific trivia question by ID"""
    try:
        question = db.get_trivia_question_by_id(question_id)
        if question:
            return jsonify(question)
        else:
            return jsonify({"error": "Question not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to get question: {str(e)}"}), 500


@app.route("/api/trivia/questions", methods=["GET"])
def get_recent_questions():
    """Get recent trivia questions"""
    try:
        limit = request.args.get("limit", 20, type=int)
        pokemon_id = request.args.get("pokemon_id", type=int)
        
        if pokemon_id:
            questions = db.get_questions_by_pokemon(pokemon_id, limit)
        else:
            questions = db.get_recent_questions(limit)
        
        return jsonify({"questions": questions, "count": len(questions)})

    except Exception as e:
        return jsonify({"error": f"Failed to get questions: {str(e)}"}), 500


# Player management endpoints
@app.route("/api/players", methods=["POST"])
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


@app.route("/api/players", methods=["GET"])
def get_all_players():
    """Get all players"""
    try:
        players = db.get_all_players()
        return jsonify({"players": players, "count": len(players)})

    except Exception as e:
        return jsonify({"error": f"Failed to get players: {str(e)}"}), 500


@app.route("/api/players/<int:player_id>", methods=["GET"])
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


@app.route("/api/players/<int:player_id>/wins", methods=["GET"])
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


# Game session management endpoints
@app.route("/api/sessions", methods=["POST"])
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


@app.route("/api/sessions/<int:session_id>", methods=["GET"])
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


@app.route("/api/sessions/<int:session_id>", methods=["PUT"])
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
            from datetime import datetime
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
                import json
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


@app.route("/api/players/<int:player_id>/sessions", methods=["GET"])
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


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
