from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from services.pokemon_fetcher import fetch_pokemon_data
from services.database import PokemonDatabase
from ai import TriviaGenerator
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

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

        return jsonify({"questions": questions, "count": len(questions)})

    except Exception as e:
        return jsonify({"error": f"Failed to generate trivia batch: {str(e)}"}), 500


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
