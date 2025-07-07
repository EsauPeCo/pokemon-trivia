import sqlite3
import json
import os
from typing import List, Dict, Any, Optional


class PokemonDatabase:
    def __init__(self, db_path: str = "data/pokemon.db"):
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

            -- Trivia questions table
            CREATE TABLE IF NOT EXISTS trivia_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL, -- JSON array of answer options
                correct_answer TEXT NOT NULL,
                question_type TEXT NOT NULL, -- 'basic_info', 'stats', 'moves', 'evolution', 'general'
                difficulty TEXT NOT NULL, -- 'easy', 'medium', 'hard'
                focus TEXT, -- Optional focus area for general questions
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id)
            );

            -- Players table
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Game sessions table
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP NULL,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                is_perfect_score BOOLEAN DEFAULT 0, -- 1 if 100% correct (win condition)
                difficulty TEXT, -- 'easy', 'medium', 'hard', or 'mixed'
                session_type TEXT NOT NULL, -- 'random', 'specific_pokemon', 'batch', 'custom'
                metadata TEXT, -- JSON for additional session data (pokemon_ids, focus areas, etc.)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            );

            -- Player Pokemon wins table (tracks which Pokemon each player has beaten with 100% score)
            CREATE TABLE IF NOT EXISTS player_pokemon_wins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL, -- Reference to the winning session
                difficulty TEXT NOT NULL, -- Difficulty when the Pokemon was beaten
                questions_count INTEGER NOT NULL, -- How many questions were answered perfectly
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, pokemon_id, difficulty), -- Prevent duplicate wins for same Pokemon/difficulty
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
                FOREIGN KEY (session_id) REFERENCES game_sessions (id)
            );

            -- Indexes for fast queries
            CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon (name);
            CREATE INDEX IF NOT EXISTS idx_trivia_questions_pokemon_id ON trivia_questions (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_trivia_questions_type ON trivia_questions (question_type);
            CREATE INDEX IF NOT EXISTS idx_trivia_questions_difficulty ON trivia_questions (difficulty);
            CREATE INDEX IF NOT EXISTS idx_pokemon_abilities_pokemon_id ON pokemon_abilities (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_pokemon_moves_pokemon_id ON pokemon_moves (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_pokemon_types_pokemon_id ON pokemon_types (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_players_name ON players (name);
            CREATE INDEX IF NOT EXISTS idx_game_sessions_player_id ON game_sessions (player_id);
            CREATE INDEX IF NOT EXISTS idx_game_sessions_start_time ON game_sessions (start_time);
            CREATE INDEX IF NOT EXISTS idx_game_sessions_session_type ON game_sessions (session_type);
            CREATE INDEX IF NOT EXISTS idx_game_sessions_perfect_score ON game_sessions (is_perfect_score);
            CREATE INDEX IF NOT EXISTS idx_player_pokemon_wins_player ON player_pokemon_wins (player_id);
            CREATE INDEX IF NOT EXISTS idx_player_pokemon_wins_pokemon ON player_pokemon_wins (pokemon_id);
            CREATE INDEX IF NOT EXISTS idx_player_pokemon_wins_difficulty ON player_pokemon_wins (difficulty);
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

    # Trivia Questions Methods
    def insert_trivia_question(self, question_data: Dict[str, Any]) -> int:
        """Insert a new trivia question and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trivia_questions 
                (pokemon_id, question, options, correct_answer, question_type, difficulty, focus)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                question_data['pokemon_id'],
                question_data['question'],
                json.dumps(question_data['options']),  # Store options as JSON
                question_data['correct_answer'],
                question_data['question_type'],
                question_data['difficulty'],
                question_data.get('focus')  # Optional field
            ))
            
            return cursor.lastrowid

    def get_trivia_question_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get a trivia question by its ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tq.*, p.name as pokemon_name
                FROM trivia_questions tq
                JOIN pokemon p ON tq.pokemon_id = p.id
                WHERE tq.id = ?
            """, (question_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            question = dict(row)
            # Parse options from JSON
            question['options'] = json.loads(question['options'])
            
            return question

    def update_question_rating(self, question_id: int, rating_type: str) -> bool:
        """Update the like or dislike count for a question"""
        if rating_type not in ['like', 'dislike']:
            return False
            
        column = 'likes' if rating_type == 'like' else 'dislikes'
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE trivia_questions 
                SET {column} = {column} + 1 
                WHERE id = ?
            """, (question_id,))
            
            return cursor.rowcount > 0

    def get_questions_by_pokemon(self, pokemon_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trivia questions for a specific Pokemon"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tq.*, p.name as pokemon_name
                FROM trivia_questions tq
                JOIN pokemon p ON tq.pokemon_id = p.id
                WHERE tq.pokemon_id = ?
                ORDER BY tq.created_at DESC
                LIMIT ?
            """, (pokemon_id, limit))
            
            questions = []
            for row in cursor.fetchall():
                question = dict(row)
                question['options'] = json.loads(question['options'])
                questions.append(question)
            
            return questions

    def get_recent_questions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently generated trivia questions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tq.*, p.name as pokemon_name
                FROM trivia_questions tq
                JOIN pokemon p ON tq.pokemon_id = p.id
                ORDER BY tq.created_at DESC
                LIMIT ?
            """, (limit,))
            
            questions = []
            for row in cursor.fetchall():
                question = dict(row)
                question['options'] = json.loads(question['options'])
                questions.append(question)
            
            return questions

    # Player Methods
    def create_player(self, name: str) -> int:
        """Create a new player and return their ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO players (name)
                VALUES (?)
            """, (name,))
            
            return cursor.lastrowid

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Get a player by their ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM players WHERE id = ?
            """, (player_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_player_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a player by their name"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM players WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all players"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM players ORDER BY created_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]

    # Game Session Methods
    def create_game_session(self, session_data: Dict[str, Any]) -> int:
        """Create a new game session and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO game_sessions 
                (player_id, difficulty, session_type, metadata, is_perfect_score)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_data['player_id'],
                session_data.get('difficulty'),
                session_data['session_type'],
                json.dumps(session_data.get('metadata', {})),
                session_data.get('is_perfect_score', 0)
            ))
            
            return cursor.lastrowid

    def get_game_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a game session by its ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT gs.*, p.name as player_name
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE gs.id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            session = dict(row)
            session['metadata'] = json.loads(session['metadata']) if session['metadata'] else {}
            
            return session

    def update_game_session(self, session_id: int, updates: Dict[str, Any]) -> bool:
        """Update a game session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field == 'metadata':
                    value = json.dumps(value)
                update_fields.append(f"{field} = ?")
                values.append(value)
            
            if not update_fields:
                return False
            
            values.append(session_id)
            query = f"""
                UPDATE game_sessions 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            return cursor.rowcount > 0

    def get_player_sessions(self, player_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get game sessions for a specific player"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT gs.*, p.name as player_name
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE gs.player_id = ?
                ORDER BY gs.start_time DESC
                LIMIT ?
            """, (player_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                session = dict(row)
                session['metadata'] = json.loads(session['metadata']) if session['metadata'] else {}
                sessions.append(session)
            
            return sessions

    # Pokemon Win Tracking Methods
    def record_pokemon_win(self, player_id: int, pokemon_id: int, session_id: int, difficulty: str, questions_count: int) -> bool:
        """Record that a player beat a Pokemon with 100% score"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO player_pokemon_wins 
                    (player_id, pokemon_id, session_id, difficulty, questions_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (player_id, pokemon_id, session_id, difficulty, questions_count))
                
                return True
            except sqlite3.IntegrityError:
                # Player already beat this Pokemon at this difficulty
                # Update with the latest session info
                cursor.execute("""
                    UPDATE player_pokemon_wins 
                    SET session_id = ?, questions_count = ?, achieved_at = CURRENT_TIMESTAMP
                    WHERE player_id = ? AND pokemon_id = ? AND difficulty = ?
                """, (session_id, questions_count, player_id, pokemon_id, difficulty))
                
                return True

    def get_player_pokemon_wins(self, player_id: int) -> List[Dict[str, Any]]:
        """Get all Pokemon that a player has beaten"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ppw.*, p.name as pokemon_name, p.sprite
                FROM player_pokemon_wins ppw
                JOIN pokemon p ON ppw.pokemon_id = p.id
                WHERE ppw.player_id = ?
                ORDER BY ppw.achieved_at DESC
            """, (player_id,))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_pokemon_win_count(self, player_id: int) -> int:
        """Get total number of unique Pokemon a player has beaten"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(DISTINCT pokemon_id) 
                FROM player_pokemon_wins 
                WHERE player_id = ?
            """, (player_id,))
            
            return cursor.fetchone()[0]

    def has_player_beaten_pokemon(self, player_id: int, pokemon_id: int, difficulty: str = None) -> bool:
        """Check if a player has beaten a specific Pokemon"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if difficulty:
                cursor.execute("""
                    SELECT 1 FROM player_pokemon_wins 
                    WHERE player_id = ? AND pokemon_id = ? AND difficulty = ?
                """, (player_id, pokemon_id, difficulty))
            else:
                cursor.execute("""
                    SELECT 1 FROM player_pokemon_wins 
                    WHERE player_id = ? AND pokemon_id = ?
                """, (player_id, pokemon_id))
            
            return cursor.fetchone() is not None

    def get_pokemon_leaderboard(self, pokemon_id: int) -> List[Dict[str, Any]]:
        """Get players who have beaten a specific Pokemon, ordered by difficulty and time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ppw.*, p.name as player_name,
                       CASE ppw.difficulty 
                           WHEN 'hard' THEN 3
                           WHEN 'medium' THEN 2
                           WHEN 'easy' THEN 1
                           ELSE 0
                       END as difficulty_order
                FROM player_pokemon_wins ppw
                JOIN players p ON ppw.player_id = p.id
                WHERE ppw.pokemon_id = ?
                ORDER BY difficulty_order DESC, ppw.achieved_at ASC
            """, (pokemon_id,))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_pokemon_count(self) -> int:
        """Get total number of Pokemon in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pokemon")
            return cursor.fetchone()[0]
    
    def clear_database(self):
        """Clear all data from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM player_pokemon_wins")
            cursor.execute("DELETE FROM game_sessions")
            cursor.execute("DELETE FROM players")
            cursor.execute("DELETE FROM trivia_questions")
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