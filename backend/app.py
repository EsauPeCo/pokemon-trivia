from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Sample data
pokemons = [
    {"id": 1, "name": "Bulbasaur", "type": "Grass/Poison"},
    {"id": 2, "name": "Charmander", "type": "Fire"},
    {"id": 3, "name": "Squirtle", "type": "Water"},
]


# Home route
@app.route("/")
def home():
    return "Welcome to the Pokémon-trivia API!"


# Get all Pokémon
@app.route("/api/pokemon", methods=["GET"])
def get_pokemons():
    return jsonify(pokemons)


# Get one Pokémon by ID
@app.route("/api/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    pokemon = next((p for p in pokemons if p["id"] == pokemon_id), None)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({"error": "Not found"}), 404


# Create a new Pokémon
@app.route("/api/pokemon", methods=["POST"])
def create_pokemon():
    data = request.get_json()
    new_pokemon = {"id": len(pokemons) + 1, "name": data["name"], "type": data["type"]}
    pokemons.append(new_pokemon)
    return jsonify(new_pokemon), 201


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
