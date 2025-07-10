from flask import Blueprint, jsonify, request
from services.database import PokemonDatabase
from ai import TriviaGenerator
import random

trivia_bp = Blueprint('trivia', __name__, url_prefix='/api/trivia')

# Initialize database and AI components
db = PokemonDatabase()
trivia_generator = TriviaGenerator()


@trivia_bp.route("/generate", methods=["POST"])
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


@trivia_bp.route("/generate-five", methods=["POST"])
def generate_five_trivia_questions():
    """Generate exactly 5 trivia questions for the same Pokemon with identical configuration
    
    This endpoint creates 5 diverse trivia questions about a single Pokemon, all sharing
    the same question type, difficulty level, and focus area. Each question follows the
    same format as single question generation but provides variety within the constraints.
    
    Request body should contain:
    - pokemon_id: ID of the Pokemon to generate questions for
    - question_type: Type of questions (basic_info, stats, moves, evolution, general)
    - difficulty: Difficulty level (easy, medium, hard) 
    - focus: Optional focus area for general questions
    
    Returns 5 questions with the same format as single question endpoints.
    """
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

        # Generate exactly 5 trivia questions for the same Pokemon
        questions = trivia_generator.generate_multiple_questions_same_pokemon(
            pokemon_data,
            question_type=question_type,
            difficulty=difficulty,
            focus=focus,
            count=5,  # Fixed at 5 questions
        )

        # Store each question in database and add IDs
        for question in questions:
            question_data = {
                'pokemon_id': pokemon_id,
                'question': question.get('question'),
                'options': question.get('options', []),
                'correct_answer': question.get('correct_answer'),
                'question_type': question.get('question_type', question_type),
                'difficulty': question.get('difficulty', difficulty),
                'focus': question.get('focus', focus)
            }
            
            question_id = db.insert_trivia_question(question_data)
            question['id'] = question_id

        return jsonify({
            "questions": questions,
            "count": 5,  # Always 5 questions
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon_data.get("name"),
            "configuration": {
                "question_type": question_type,
                "difficulty": difficulty,
                "focus": focus
            }
        })

    except Exception as e:
        return jsonify({"error": f"Failed to generate 5 trivia questions: {str(e)}"}), 500


@trivia_bp.route("/random", methods=["GET"])
def generate_random_trivia():
    """Generate a random trivia question from a random Pokemon"""
    try:
        difficulty = request.args.get("difficulty")

        # Get random Pokemon
        pokemon_list = db.get_pokemon_list()
        if not pokemon_list:
            return jsonify({"error": "No Pokemon found in database"}), 404

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


@trivia_bp.route("/batch", methods=["POST"])
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


@trivia_bp.route("/questions/rating", methods=["POST"])
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


@trivia_bp.route("/questions/<int:question_id>", methods=["GET"])
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


@trivia_bp.route("/questions", methods=["GET"])
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