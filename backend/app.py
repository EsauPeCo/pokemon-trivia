from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from services.pokemon_fetcher import fetch_pokemon_data
from services.database import PokemonDatabase
from ai import TriviaGenerator
from routes import static_bp, pokemon_bp, trivia_bp, players_bp, sessions_bp
import os

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:5000", "http://127.0.0.1:5000"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Pokemon Trivia API",
        "description": "A comprehensive API for Pokemon trivia game featuring AI-generated questions, player management, and game sessions",
        "version": "1.0.0",
        "contact": {
            "name": "Pokemon Trivia Team",
            "email": "support@pokemon-trivia.com"
        }
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": [
        "http"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "tags": [
        {
            "name": "pokemon",
            "description": "Pokemon data operations"
        },
        {
            "name": "trivia",
            "description": "Trivia question generation and management"
        },
        {
            "name": "players",
            "description": "Player management operations"
        },
        {
            "name": "sessions",
            "description": "Game session management"
        },
        {
            "name": "health",
            "description": "System health and status"
        }
    ]
}

# Initialize Swagger
swagger = Swagger(app, config=swagger_config, template=swagger_template)

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

# Register blueprints
app.register_blueprint(static_bp)
app.register_blueprint(pokemon_bp)
app.register_blueprint(trivia_bp)
app.register_blueprint(players_bp)
app.register_blueprint(sessions_bp)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
