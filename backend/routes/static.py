from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)


@static_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "icons", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@static_bp.route("/favicon-32x32.png")
def favicon_32():
    return send_from_directory("icons", "favicon-32x32.png", mimetype="image/png")


@static_bp.route("/")
def home():
    from services.database import PokemonDatabase
    db = PokemonDatabase()
    
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