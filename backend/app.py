from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
from services.pokemon_fetcher import fetch_pokemon_data

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


# Favicon routes
@app.route("/favicon.ico")
def favicon():
    return send_from_directory("icons", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.route("/favicon-32x32.png")
def favicon_32():
    return send_from_directory("icons", "favicon-32x32.png", mimetype="image/png")


# Fetch Pokémon data on startup
print("Fetching Pokémon data from PokeAPI...")
pokemons = fetch_pokemon_data()
print(f"Successfully fetched {len(pokemons)} Pokémon")


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
    </body>
    </html>
    """


# Get all Pokémon
@app.route("/api/pokemon", methods=["GET"])
def get_pokemons():
    # Return only essential fields for the list view
    simplified_pokemons = [
        {
            "id": pokemon["id"],
            "name": pokemon["name"],
            "sprite": pokemon["sprite"],
            "shiny_sprite": pokemon["shiny_sprite"],
        }
        for pokemon in pokemons
    ]
    return jsonify(simplified_pokemons)


# Get one Pokémon by ID
@app.route("/api/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    pokemon = next((p for p in pokemons if p["id"] == pokemon_id), None)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({"error": "Pokémon not found"}), 404


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
