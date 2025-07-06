import sqlite3
import json
import os
from typing import List, Dict, Any, Optional


class PokemonDatabase:
    def __init__(self, db_path: str = "pokemon.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
            -- Core Pokemon table
            CREATE TABLE IF NOT EXISTS pokemon (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                base_experience INTEGER,
                sprite TEXT,
                shiny_sprite TEXT,
                flavor_text TEXT,
                habitat TEXT,
                shape TEXT
            );

            -- Pokemon stats (1-to-1 relationship)
            CREATE TABLE IF NOT EXISTS pokemon_stats (
                pokemon_id INTEGER PRIMARY KEY,
                hp INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                special_attack INTEGER NOT NULL,
                special_defense INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id)
            );

            -- Normalized reference tables
            CREATE TABLE IF NOT EXISTS abilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            -- Junction tables for many-to-many relationships
            CREATE TABLE IF NOT EXISTS pokemon_abilities (
                pokemon_id INTEGER,
                ability_id INTEGER,
                slot INTEGER, -- To maintain order
                PRIMARY KEY (pokemon_id, ability_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (ability_id) REFERENCES abilities (id)
            );

            CREATE TABLE IF NOT EXISTS pokemon_moves (
                pokemon_id INTEGER,
                move_id INTEGER,
                slot INTEGER, -- To maintain order
                PRIMARY KEY (pokemon_id, move_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (move_id) REFERENCES moves (id)
            );

            CREATE TABLE IF NOT EXISTS pokemon_types (
                pokemon_id INTEGER,
                type_id INTEGER,
                slot INTEGER NOT NULL, -- To maintain order (primary/secondary)
                PRIMARY KEY (pokemon_id, type_id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (type_id) REFERENCES types (id)
            );

            -- Evolution chain (stored as JSON for simplicity)
            CREATE TABLE IF NOT EXISTS pokemon_evolution_chains (
                pokemon_id INTEGER PRIMARY KEY,
                evolution_chain_json TEXT, -- Store the complex nested structure as JSON
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id)
            );

            -- Indexes for fast queries
            CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon (name);
            CREATE INDEX IF NOT EXISTS idx_pokemon_abilities_pokemon_id ON pokemon_abilities (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_pokemon_moves_pokemon_id ON pokemon_moves (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_pokemon_types_pokemon_id ON pokemon_types (pokemon_id);
            """)
    
    def database_is_empty(self) -> bool:
        """Check if database has any Pokemon data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pokemon")
            count = cursor.fetchone()[0]
            return count == 0
    
    def insert_pokemon(self, pokemon_data: Dict[str, Any]):
        """Insert a complete Pokemon record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert main Pokemon data
            cursor.execute("""
                INSERT OR REPLACE INTO pokemon 
                (id, name, height, weight, base_experience, sprite, shiny_sprite, 
                 flavor_text, habitat, shape)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pokemon_data['id'], 
                pokemon_data['name'], 
                pokemon_data['height'],
                pokemon_data['weight'], 
                pokemon_data['base_experience'],
                pokemon_data['sprite'], 
                pokemon_data['shiny_sprite'],
                pokemon_data['flavor_text'], 
                pokemon_data['habitat'], 
                pokemon_data['shape']
            ))
            
            # Insert stats
            stats = pokemon_data['stats']
            cursor.execute("""
                INSERT OR REPLACE INTO pokemon_stats 
                (pokemon_id, hp, attack, defense, special_attack, special_defense, speed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pokemon_data['id'], 
                stats['hp'], 
                stats['attack'], 
                stats['defense'],
                stats['special-attack'], 
                stats['special-defense'], 
                stats['speed']
            ))
            
            # Insert abilities, moves, types
            self._insert_abilities(cursor, pokemon_data['id'], pokemon_data['abilities'])
            self._insert_moves(cursor, pokemon_data['id'], pokemon_data['moves'])
            self._insert_types(cursor, pokemon_data['id'], pokemon_data['types'])
            
            # Store evolution chain as JSON
            evolution_chain_json = json.dumps(pokemon_data.get('evolution_chain')) if pokemon_data.get('evolution_chain') else None
            cursor.execute("""
                INSERT OR REPLACE INTO pokemon_evolution_chains (pokemon_id, evolution_chain_json)
                VALUES (?, ?)
            """, (pokemon_data['id'], evolution_chain_json))
    
    def get_pokemon_list(self) -> List[Dict[str, Any]]:
        """Fast query for /api/pokemon endpoint - only essential fields"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, sprite, shiny_sprite 
                FROM pokemon 
                ORDER BY id
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """Fast query for /api/pokemon/<id> endpoint - complete Pokemon data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get main Pokemon data with stats
            cursor.execute("""
                SELECT p.*, ps.hp, ps.attack, ps.defense, ps.special_attack, 
                       ps.special_defense, ps.speed, pec.evolution_chain_json
                FROM pokemon p
                JOIN pokemon_stats ps ON p.id = ps.pokemon_id
                LEFT JOIN pokemon_evolution_chains pec ON p.id = pec.pokemon_id
                WHERE p.id = ?
            """, (pokemon_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            pokemon = dict(row)
            
            # Get abilities in order
            cursor.execute("""
                SELECT a.name FROM abilities a
                JOIN pokemon_abilities pa ON a.id = pa.ability_id
                WHERE pa.pokemon_id = ?
                ORDER BY pa.slot
            """, (pokemon_id,))
            pokemon['abilities'] = [row[0] for row in cursor.fetchall()]
            
            # Get moves in order
            cursor.execute("""
                SELECT m.name FROM moves m
                JOIN pokemon_moves pm ON m.id = pm.move_id
                WHERE pm.pokemon_id = ?
                ORDER BY pm.slot
            """, (pokemon_id,))
            pokemon['moves'] = [row[0] for row in cursor.fetchall()]
            
            # Get types in order
            cursor.execute("""
                SELECT t.name FROM types t
                JOIN pokemon_types pt ON t.id = pt.type_id
                WHERE pt.pokemon_id = ?
                ORDER BY pt.slot
            """, (pokemon_id,))
            pokemon['types'] = [row[0] for row in cursor.fetchall()]
            
            # Format stats object to match original structure
            pokemon['stats'] = {
                'hp': pokemon['hp'],
                'attack': pokemon['attack'],
                'defense': pokemon['defense'],
                'special-attack': pokemon['special_attack'],
                'special-defense': pokemon['special_defense'],
                'speed': pokemon['speed']
            }
            
            # Parse evolution chain JSON
            if pokemon['evolution_chain_json']:
                pokemon['evolution_chain'] = json.loads(pokemon['evolution_chain_json'])
            else:
                pokemon['evolution_chain'] = None
            
            # Clean up extra fields that shouldn't be in response
            for field in ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed', 'evolution_chain_json']:
                pokemon.pop(field, None)
            
            return pokemon
    
    def _insert_abilities(self, cursor, pokemon_id: int, abilities: List[str]):
        """Helper to insert abilities with proper relationship"""
        # Clear existing relationships
        cursor.execute("DELETE FROM pokemon_abilities WHERE pokemon_id = ?", (pokemon_id,))
        
        for slot, ability_name in enumerate(abilities):
            # Insert ability if not exists
            cursor.execute("INSERT OR IGNORE INTO abilities (name) VALUES (?)", (ability_name,))
            
            # Get ability ID
            cursor.execute("SELECT id FROM abilities WHERE name = ?", (ability_name,))
            ability_id = cursor.fetchone()[0]
            
            # Link to Pokemon
            cursor.execute("""
                INSERT INTO pokemon_abilities (pokemon_id, ability_id, slot)
                VALUES (?, ?, ?)
            """, (pokemon_id, ability_id, slot))
    
    def _insert_moves(self, cursor, pokemon_id: int, moves: List[str]):
        """Helper to insert moves with proper relationship"""
        # Clear existing relationships
        cursor.execute("DELETE FROM pokemon_moves WHERE pokemon_id = ?", (pokemon_id,))
        
        for slot, move_name in enumerate(moves):
            # Insert move if not exists
            cursor.execute("INSERT OR IGNORE INTO moves (name) VALUES (?)", (move_name,))
            
            # Get move ID
            cursor.execute("SELECT id FROM moves WHERE name = ?", (move_name,))
            move_id = cursor.fetchone()[0]
            
            # Link to Pokemon
            cursor.execute("""
                INSERT INTO pokemon_moves (pokemon_id, move_id, slot)
                VALUES (?, ?, ?)
            """, (pokemon_id, move_id, slot))
    
    def _insert_types(self, cursor, pokemon_id: int, types: List[str]):
        """Helper to insert types with proper relationship"""
        # Clear existing relationships
        cursor.execute("DELETE FROM pokemon_types WHERE pokemon_id = ?", (pokemon_id,))
        
        for slot, type_name in enumerate(types):
            # Insert type if not exists
            cursor.execute("INSERT OR IGNORE INTO types (name) VALUES (?)", (type_name,))
            
            # Get type ID
            cursor.execute("SELECT id FROM types WHERE name = ?", (type_name,))
            type_id = cursor.fetchone()[0]
            
            # Link to Pokemon
            cursor.execute("""
                INSERT INTO pokemon_types (pokemon_id, type_id, slot)
                VALUES (?, ?, ?)
            """, (pokemon_id, type_id, slot))

    def get_pokemon_count(self) -> int:
        """Get total number of Pokemon in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pokemon")
            return cursor.fetchone()[0]
    
    def clear_database(self):
        """Clear all Pokemon data from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pokemon_evolution_chains")
            cursor.execute("DELETE FROM pokemon_types")
            cursor.execute("DELETE FROM pokemon_moves")
            cursor.execute("DELETE FROM pokemon_abilities")
            cursor.execute("DELETE FROM pokemon_stats")
            cursor.execute("DELETE FROM pokemon")
            cursor.execute("DELETE FROM abilities")
            cursor.execute("DELETE FROM moves")
            cursor.execute("DELETE FROM types")
            conn.commit() 