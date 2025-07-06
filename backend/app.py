from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Function to fetch and clean Pokémon data from PokeAPI
def fetch_pokemon_data():
    """Fetch the first 151 Pokémon from PokeAPI"""
    pokemons = []
    
    try:
        # Fetch the first 151 Pokémon (IDs 1-151)
        for pokemon_id in range(1, 152):
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
            if response.status_code == 200:
                pokemon_data = response.json()
                
                # Extract relevant information
                pokemon = {
                    "id": pokemon_data["id"],
                    "name": pokemon_data["name"].title(),
                    "types": [type_info["type"]["name"].title() for type_info in pokemon_data["types"]],
                    "height": pokemon_data["height"] / 10,  # Convert to meters
                    "weight": pokemon_data["weight"] / 10,  # Convert to kg
                    "sprite": pokemon_data["sprites"]["other"]["official-artwork"]["front_default"],
                    "shiny_sprite": pokemon_data["sprites"]["other"]["official-artwork"]["front_shiny"],
                    "abilities": [ability["ability"]["name"].title() for ability in pokemon_data["abilities"]],
                    "base_experience": pokemon_data["base_experience"],
                    "moves": [move["move"]["name"].title() for move in pokemon_data["moves"]],
                    "stats": {
                        stat["stat"]["name"]: stat["base_stat"] 
                        for stat in pokemon_data["stats"]
                    }
                }
                pokemons.append(pokemon)
                print(f"Fetched {pokemon['name']} (ID: {pokemon['id']})")
            else:
                print(f"Failed to fetch Pokémon with ID {pokemon_id}")
                
    except Exception as e:
        print(f"Error fetching Pokémon data: {e}")
        return []
    
    return pokemons

# Fetch Pokémon data on startup
print("Fetching Pokémon data from PokeAPI...")
pokemons = fetch_pokemon_data()
print(f"Successfully fetched {len(pokemons)} Pokémon")

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
    return jsonify({"error": "Pokémon not found"}), 404


# Get random Pokémon for trivia
@app.route("/api/pokemon/random", methods=["GET"])
def get_random_pokemon():
    import random
    if pokemons:
        random_pokemon = random.choice(pokemons)
        return jsonify(random_pokemon)
    return jsonify({"error": "No Pokémon available"}), 404


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
