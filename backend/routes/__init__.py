"""
Routes package for Pokemon Trivia API
"""

from .static import static_bp
from .pokemon import pokemon_bp
from .trivia import trivia_bp
from .players import players_bp
from .sessions import sessions_bp

__all__ = ['static_bp', 'pokemon_bp', 'trivia_bp', 'players_bp', 'sessions_bp'] 