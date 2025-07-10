from flask import Flask
from flask_cors import CORS
from services.pokemon_fetcher import fetch_pokemon_data
from services.database import PokemonDatabase
from ai import TriviaGenerator
from routes import static_bp, pokemon_bp, trivia_bp, players_bp, sessions_bp
import os

app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:5173"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

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
