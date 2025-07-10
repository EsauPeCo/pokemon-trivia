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
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 600px; 
                margin: 50px auto; 
                padding: 20px; 
                background: #f5f5f5; 
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .api-link {{ 
                display: inline-block; 
                background: #007acc; 
                color: white; 
                padding: 12px 24px; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
                font-weight: bold;
                transition: background 0.3s;
            }}
            .api-link:hover {{ 
                background: #005fa3; 
            }}
            .stats {{ 
                background: #e8f4f8; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 20px 0; 
            }}
        </style>
    </head>
    <body>
        <h1>🎮 Pokémon Trivia API</h1>
        <p>Welcome to the Pokémon Trivia API! This is the backend service that powers the Pokémon trivia game.</p>
        
        <div class="stats">
            <h3>📊 System Status</h3>
            <p><strong>Database:</strong> {} Pokémon loaded and ready!</p>
            <p><strong>Status:</strong> ✅ Online and operational</p>
        </div>
        
        <h3>📚 API Documentation</h3>
        <p>Explore our complete API documentation with interactive testing capabilities:</p>
        <a href="/apidocs/" class="api-link">🚀 Go to API Documentation (/apidocs/)</a>
        
        <h3>🎯 Available Features</h3>
        <ul>
            <li><strong>Pokémon Data:</strong> Access detailed information for 1000+ Pokémon</li>
            <li><strong>AI Trivia:</strong> Generate smart trivia questions using Google Gemini</li>
            <li><strong>Player Management:</strong> Create and track players (max 3)</li>
            <li><strong>Game Sessions:</strong> Manage trivia game sessions with scoring</li>
            <li><strong>Question Rating:</strong> Like/dislike system for generated questions</li>
        </ul>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="text-align: center; color: #666; font-size: 14px;">
            Pokémon Trivia API v1.0.0 | 
            <a href="/apidocs/" style="color: #007acc;">Interactive Documentation</a> |
            <a href="/apispec_1.json" style="color: #007acc;">OpenAPI Spec</a>
        </p>
    </body>
    </html>
    """.format(
        db.get_pokemon_count()
    ) 