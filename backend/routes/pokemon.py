from flask import Blueprint, jsonify
from services.database import PokemonDatabase

pokemon_bp = Blueprint('pokemon', __name__, url_prefix='/api')

# Initialize database instance
db = PokemonDatabase()


@pokemon_bp.route("/pokemon", methods=["GET"])
def get_pokemons():
    """Get all Pokémon - now using database
    ---
    tags:
      - pokemon
    summary: Get all Pokemon
    description: Retrieve a list of all Pokemon from the database with essential information
    responses:
      200:
        description: List of Pokemon successfully retrieved
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Pokemon ID
                example: 1
              name:
                type: string
                description: Pokemon name
                example: "bulbasaur"
              types:
                type: array
                items:
                  type: string
                description: Pokemon types
                example: ["grass", "poison"]
              height:
                type: integer
                description: Pokemon height in decimetres
                example: 7
              weight:
                type: integer
                description: Pokemon weight in hectograms
                example: 69
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    # Return only essential fields for the list view
    simplified_pokemons = db.get_pokemon_list()
    return jsonify(simplified_pokemons)


@pokemon_bp.route("/pokemon/<int:pokemon_id>", methods=["GET"])
def get_pokemon(pokemon_id):
    """Get one Pokémon by ID - now using database
    ---
    tags:
      - pokemon
    summary: Get Pokemon by ID
    description: Retrieve detailed information for a specific Pokemon by its ID
    parameters:
      - name: pokemon_id
        in: path
        type: integer
        required: true
        description: The ID of the Pokemon to retrieve
        example: 1
    responses:
      200:
        description: Pokemon details successfully retrieved
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Pokemon ID
              example: 1
            name:
              type: string
              description: Pokemon name
              example: "bulbasaur"
            types:
              type: array
              items:
                type: string
              description: Pokemon types
              example: ["grass", "poison"]
            height:
              type: integer
              description: Pokemon height in decimetres
              example: 7
            weight:
              type: integer
              description: Pokemon weight in hectograms
              example: 69
            stats:
              type: object
              description: Pokemon base stats
              properties:
                hp:
                  type: integer
                  example: 45
                attack:
                  type: integer
                  example: 49
                defense:
                  type: integer
                  example: 49
                special-attack:
                  type: integer
                  example: 65
                special-defense:
                  type: integer
                  example: 65
                speed:
                  type: integer
                  example: 45
            moves:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                    example: "tackle"
                  level_learned:
                    type: integer
                    example: 1
              description: Pokemon moves
            sprites:
              type: object
              description: Pokemon sprite URLs
              properties:
                front_default:
                  type: string
                  example: "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png"
      404:
        description: Pokemon not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Pokémon not found"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    pokemon = db.get_pokemon_by_id(pokemon_id)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({"error": "Pokémon not found"}), 404


@pokemon_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint
    ---
    tags:
      - health
    summary: System health check
    description: Check the health status of the Pokemon API and database connectivity
    responses:
      200:
        description: System is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              description: System status
              example: "healthy"
            pokemon_count:
              type: integer
              description: Total number of Pokemon in database
              example: 1010
            database:
              type: string
              description: Database connection status
              example: "connected"
      500:
        description: System is unhealthy
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    return jsonify(
        {
            "status": "healthy",
            "pokemon_count": db.get_pokemon_count(),
            "database": "connected",
        }
    ) 