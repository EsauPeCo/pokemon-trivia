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
    """Generate a trivia question for a specific Pokemon
    ---
    tags:
      - trivia
    summary: Generate trivia question
    description: Generate a single AI-powered trivia question for a specific Pokemon
    parameters:
      - name: body
        in: body
        required: true
        description: Trivia generation parameters
        schema:
          type: object
          required:
            - pokemon_id
          properties:
            pokemon_id:
              type: integer
              description: ID of the Pokemon to generate a question about
              example: 25
            question_type:
              type: string
              description: Type of question to generate
              enum: ["basic_info", "stats", "moves", "evolution", "general"]
              default: "general"
              example: "stats"
            difficulty:
              type: string
              description: Difficulty level of the question
              enum: ["easy", "medium", "hard"]
              default: "medium"
              example: "medium"
            focus:
              type: string
              description: Specific focus area for general questions
              example: "abilities"
    responses:
      200:
        description: Trivia question generated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Question ID
              example: 123
            question:
              type: string
              description: The trivia question
              example: "What is Pikachu's base Attack stat?"
            options:
              type: array
              items:
                type: string
              description: Multiple choice options
              example: ["55", "45", "65", "40"]
            correct_answer:
              type: string
              description: The correct answer
              example: "55"
            question_type:
              type: string
              description: Type of the generated question
              example: "stats"
            difficulty:
              type: string
              description: Difficulty level of the question
              example: "medium"
            pokemon_id:
              type: integer
              description: ID of the Pokemon the question is about
              example: 25
            pokemon_name:
              type: string
              description: Name of the Pokemon
              example: "pikachu"
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "pokemon_id is required"
      404:
        description: Pokemon not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Pokemon not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate trivia: AI service unavailable"
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
    ---
    tags:
      - trivia
    summary: Generate 5 trivia questions
    description: Generate exactly 5 diverse AI-powered trivia questions about a single Pokemon with identical configuration settings
    parameters:
      - name: body
        in: body
        required: true
        description: Trivia generation parameters for 5 questions
        schema:
          type: object
          required:
            - pokemon_id
          properties:
            pokemon_id:
              type: integer
              description: ID of the Pokemon to generate questions about
              example: 25
            question_type:
              type: string
              description: Type of questions to generate (all 5 will be this type)
              enum: ["basic_info", "stats", "moves", "evolution", "general"]
              default: "general"
              example: "stats"
            difficulty:
              type: string
              description: Difficulty level of all questions
              enum: ["easy", "medium", "hard"]
              default: "medium"
              example: "medium"
            focus:
              type: string
              description: Specific focus area for general questions
              example: "abilities"
    responses:
      200:
        description: 5 trivia questions generated successfully
        schema:
          type: object
          properties:
            questions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Question ID
                    example: 123
                  question:
                    type: string
                    description: The trivia question
                    example: "What is Pikachu's base Attack stat?"
                  options:
                    type: array
                    items:
                      type: string
                    description: Multiple choice options
                    example: ["55", "45", "65", "40"]
                  correct_answer:
                    type: string
                    description: The correct answer
                    example: "55"
                  question_type:
                    type: string
                    description: Type of the question
                    example: "stats"
                  difficulty:
                    type: string
                    description: Difficulty level
                    example: "medium"
              description: Array of exactly 5 trivia questions
            count:
              type: integer
              description: Number of questions (always 5)
              example: 5
            pokemon_id:
              type: integer
              description: ID of the Pokemon
              example: 25
            pokemon_name:
              type: string
              description: Name of the Pokemon
              example: "pikachu"
            configuration:
              type: object
              properties:
                question_type:
                  type: string
                  example: "stats"
                difficulty:
                  type: string
                  example: "medium"
                focus:
                  type: string
                  example: "abilities"
              description: Configuration used for all questions
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "pokemon_id is required"
      404:
        description: Pokemon not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Pokemon not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate 5 trivia questions: AI service unavailable"
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
    """Generate a random trivia question from a random Pokemon
    ---
    tags:
      - trivia
    summary: Generate random trivia question
    description: Generate a random trivia question about a randomly selected Pokemon
    parameters:
      - name: difficulty
        in: query
        type: string
        description: Difficulty level (optional)
        enum: ["easy", "medium", "hard"]
        example: "medium"
    responses:
      200:
        description: Random trivia question generated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Question ID
              example: 124
            question:
              type: string
              description: The trivia question
              example: "Which type is Charizard weak against?"
            options:
              type: array
              items:
                type: string
              description: Multiple choice options
              example: ["Water", "Grass", "Electric", "Fire"]
            correct_answer:
              type: string
              description: The correct answer
              example: "Water"
            question_type:
              type: string
              description: Type of the generated question
              example: "general"
            difficulty:
              type: string
              description: Difficulty level of the question
              example: "medium"
            pokemon_id:
              type: integer
              description: ID of the randomly selected Pokemon
              example: 6
            pokemon_name:
              type: string
              description: Name of the Pokemon
              example: "charizard"
      404:
        description: No Pokemon found in database
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No Pokemon found in database"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate random trivia: AI service unavailable"
    """
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
    """Generate multiple trivia questions
    ---
    tags:
      - trivia
    summary: Generate batch of trivia questions
    description: Generate multiple trivia questions with flexible configuration (max 20 questions)
    parameters:
      - name: body
        in: body
        required: true
        description: Batch trivia generation parameters
        schema:
          type: object
          properties:
            count:
              type: integer
              description: Number of questions to generate (max 20)
              minimum: 1
              maximum: 20
              default: 5
              example: 10
            difficulty:
              type: string
              description: Difficulty level for all questions
              enum: ["easy", "medium", "hard"]
              example: "medium"
            pokemon_ids:
              type: array
              items:
                type: integer
              description: Specific Pokemon IDs to generate questions for (optional, uses random if empty)
              example: [1, 4, 7, 25, 150]
    responses:
      200:
        description: Batch of trivia questions generated successfully
        schema:
          type: object
          properties:
            questions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Question ID
                    example: 125
                  question:
                    type: string
                    description: The trivia question
                    example: "What evolution does Bulbasaur become?"
                  options:
                    type: array
                    items:
                      type: string
                    description: Multiple choice options
                    example: ["Ivysaur", "Venusaur", "Oddish", "Bellsprout"]
                  correct_answer:
                    type: string
                    description: The correct answer
                    example: "Ivysaur"
                  question_type:
                    type: string
                    description: Type of the question
                    example: "evolution"
                  difficulty:
                    type: string
                    description: Difficulty level
                    example: "medium"
                  pokemon_id:
                    type: integer
                    description: ID of the Pokemon the question is about
                    example: 1
                  pokemon_name:
                    type: string
                    description: Name of the Pokemon
                    example: "bulbasaur"
              description: Array of generated trivia questions
            count:
              type: integer
              description: Number of questions generated
              example: 10
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              examples:
                count_limit: "Maximum 20 questions per batch"
      404:
        description: No valid Pokemon found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No valid Pokemon found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to generate trivia batch: AI service unavailable"
    """
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
    """Update rating for multiple trivia questions
    ---
    tags:
      - trivia
    summary: Update question ratings
    description: Update like/dislike ratings for multiple trivia questions in batch (max 50 updates)
    parameters:
      - name: body
        in: body
        required: true
        description: Batch rating update data
        schema:
          type: object
          required:
            - updates
          properties:
            updates:
              type: array
              items:
                type: object
                required:
                  - question_id
                  - action
                properties:
                  question_id:
                    type: integer
                    description: ID of the question to rate
                    example: 123
                  action:
                    type: string
                    description: Rating action
                    enum: ["like", "dislike"]
                    example: "like"
              description: Array of rating updates (max 50)
              maxItems: 50
              example: [{"question_id": 123, "action": "like"}, {"question_id": 124, "action": "dislike"}]
    responses:
      200:
        description: All ratings updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Processed 2 successful updates"
            results:
              type: array
              items:
                type: object
                properties:
                  question_id:
                    type: integer
                    example: 123
                  action:
                    type: string
                    example: "like"
                  success:
                    type: boolean
                    example: true
                  likes:
                    type: integer
                    description: Updated like count
                    example: 15
                  dislikes:
                    type: integer
                    description: Updated dislike count
                    example: 3
              description: Array of successful updates
            successful_count:
              type: integer
              description: Number of successful updates
              example: 2
            error_count:
              type: integer
              description: Number of failed updates
              example: 0
      207:
        description: Partial success (some updates failed)
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Processed 1 successful updates"
            results:
              type: array
              items:
                type: object
                properties:
                  question_id:
                    type: integer
                    example: 123
                  action:
                    type: string
                    example: "like"
                  success:
                    type: boolean
                    example: true
                  likes:
                    type: integer
                    example: 15
                  dislikes:
                    type: integer
                    example: 3
            errors:
              type: array
              items:
                type: object
                properties:
                  error:
                    type: string
                    example: "Question not found"
                  question_id:
                    type: integer
                    example: 999
                  action:
                    type: string
                    example: "like"
            successful_count:
              type: integer
              example: 1
            error_count:
              type: integer
              example: 1
      400:
        description: Invalid input data
        schema:
          type: object
          properties:
            error:
              type: string
              examples:
                missing_updates: "updates array is required"
                invalid_type: "updates must be an array"
                batch_limit: "Maximum 50 updates per batch"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to update question ratings: Database error"
    """
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
    """Get a specific trivia question by ID
    ---
    tags:
      - trivia
    summary: Get trivia question by ID
    description: Retrieve details for a specific trivia question including ratings
    parameters:
      - name: question_id
        in: path
        type: integer
        required: true
        description: The ID of the trivia question to retrieve
        example: 123
    responses:
      200:
        description: Trivia question successfully retrieved
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Question ID
              example: 123
            question:
              type: string
              description: The trivia question
              example: "What is Pikachu's base Attack stat?"
            options:
              type: array
              items:
                type: string
              description: Multiple choice options
              example: ["55", "45", "65", "40"]
            correct_answer:
              type: string
              description: The correct answer
              example: "55"
            question_type:
              type: string
              description: Type of the question
              example: "stats"
            difficulty:
              type: string
              description: Difficulty level
              example: "medium"
            pokemon_id:
              type: integer
              description: ID of the Pokemon the question is about
              example: 25
            pokemon_name:
              type: string
              description: Name of the Pokemon
              example: "pikachu"
            likes:
              type: integer
              description: Number of likes
              example: 15
            dislikes:
              type: integer
              description: Number of dislikes
              example: 3
            created_at:
              type: string
              format: date-time
              description: Question creation timestamp
              example: "2024-01-15T14:30:00"
      404:
        description: Question not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Question not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to get question: Database error"
    """
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
    """Get recent trivia questions
    ---
    tags:
      - trivia
    summary: Get recent trivia questions
    description: Retrieve recent trivia questions with optional filtering by Pokemon
    parameters:
      - name: limit
        in: query
        type: integer
        description: Maximum number of questions to return
        default: 20
        minimum: 1
        maximum: 100
        example: 20
      - name: pokemon_id
        in: query
        type: integer
        description: Filter questions by specific Pokemon ID
        example: 25
    responses:
      200:
        description: Recent trivia questions successfully retrieved
        schema:
          type: object
          properties:
            questions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: Question ID
                    example: 123
                  question:
                    type: string
                    description: The trivia question
                    example: "What is Pikachu's base Attack stat?"
                  options:
                    type: array
                    items:
                      type: string
                    description: Multiple choice options
                    example: ["55", "45", "65", "40"]
                  correct_answer:
                    type: string
                    description: The correct answer
                    example: "55"
                  question_type:
                    type: string
                    description: Type of the question
                    example: "stats"
                  difficulty:
                    type: string
                    description: Difficulty level
                    example: "medium"
                  pokemon_id:
                    type: integer
                    description: ID of the Pokemon the question is about
                    example: 25
                  pokemon_name:
                    type: string
                    description: Name of the Pokemon
                    example: "pikachu"
                  likes:
                    type: integer
                    description: Number of likes
                    example: 15
                  dislikes:
                    type: integer
                    description: Number of dislikes
                    example: 3
                  created_at:
                    type: string
                    format: date-time
                    description: Question creation timestamp
                    example: "2024-01-15T14:30:00"
              description: Array of recent trivia questions
            count:
              type: integer
              description: Number of questions returned
              example: 15
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to get questions: Database error"
    """
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