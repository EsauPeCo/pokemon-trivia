from flask import Blueprint, jsonify
from services.database import PokemonDatabase

pokemon_bp = Blueprint('pokemon', __name__, url_prefix='/api')

# Initialize database instance
db = PokemonDatabase()


@pokemon_bp.route("/pokemon", methods=["GET"])
def get_pokemons():
    """Get all Pokémon - now using database"""
    # Return only essential fields for the list view
    simplified_pokemons = db.get_pokemon_list()
    return jsonify(simplified_pokemons)


@pokemon_bp.route("/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    """Get one Pokémon by ID - now using database"""
    pokemon = db.get_pokemon_by_id(pokemon_id)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({"error": "Pokémon not found"}), 404


@pokemon_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "pokemon_count": db.get_pokemon_count(),
            "database": "connected",
        }
    ) 