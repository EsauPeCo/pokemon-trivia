from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from services.pokemon_fetcher import fetch_pokemon_data
from services.database import PokemonDatabase

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Initialize database
db = PokemonDatabase()

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
    return send_from_directory("icons", "favicon.ico", mimetype="image/vnd.microsoft.icon")


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
    """.format(db.get_pokemon_count())


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
    return jsonify({
        "status": "healthy",
        "pokemon_count": db.get_pokemon_count(),
        "database": "connected"
    })



# Run the app
if __name__ == "__main__":
    app.run(debug=True)
