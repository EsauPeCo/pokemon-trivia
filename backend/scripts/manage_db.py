#!/usr/bin/env python3
"""
Database management script for Pokemon Trivia
Usage: python manage_db.py [options]
"""
import argparse
import os
import sys
from services.database import PokemonDatabase
from services.pokemon_fetcher import fetch_pokemon_data


def reset_database():
    """Delete and recreate the database"""
    db_path = "data/pokemon.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Deleted {db_path}")
    
    db = PokemonDatabase()
    print("✓ Created new empty database")
    return db


def load_pokemon_data(db):
    """Fetch and load Pokemon data"""
    print("⏳ Fetching Pokemon data from PokeAPI...")
    pokemons = fetch_pokemon_data()
    
    if not pokemons:
        print("❌ Failed to fetch Pokemon data!")
        return False
    
    print(f"⏳ Loading {len(pokemons)} Pokemon into database...")
    for i, pokemon in enumerate(pokemons, 1):
        db.insert_pokemon(pokemon)
        if i % 10 == 0:
            print(f"   Loaded {i}/{len(pokemons)} Pokemon...")
    
    print(f"✓ Successfully loaded {len(pokemons)} Pokemon!")
    return True


def show_stats():
    """Show database statistics"""
    db = PokemonDatabase()
    count = db.get_pokemon_count()
    
    if count == 0:
        print("📊 Database is empty")
        return
    
    print(f"📊 Database Statistics:")
    print(f"   Pokemon: {count}")
    
    # Show database file size
    db_path = "data/pokemon.db"
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"   Database size: {size_mb:.2f} MB")
    
    # Show sample data
    if count > 0:
        sample = db.get_pokemon_by_id(1)
        if sample:
            print(f"   Sample Pokemon: {sample['name']}")
            print(f"     Types: {', '.join(sample['types'])}")
            print(f"     Abilities: {', '.join(sample['abilities'])}")
            print(f"     Moves: {len(sample['moves'])} moves")


def clear_database():
    """Clear all data from database"""
    db = PokemonDatabase()
    db.clear_database()
    print("✓ Cleared all data from database")


def verify_database():
    """Verify database integrity"""
    db = PokemonDatabase()
    count = db.get_pokemon_count()
    
    if count == 0:
        print("⚠️  Database is empty")
        return False
    
    print(f"⏳ Verifying {count} Pokemon...")
    
    # Check for missing data
    issues = []
    for pokemon_id in range(1, 152):  # Gen 1 Pokemon
        pokemon = db.get_pokemon_by_id(pokemon_id)
        if not pokemon:
            issues.append(f"Missing Pokemon #{pokemon_id}")
        else:
            # Check required fields
            if not pokemon.get('name'):
                issues.append(f"Pokemon #{pokemon_id} missing name")
            if not pokemon.get('types'):
                issues.append(f"Pokemon #{pokemon_id} missing types")
            if not pokemon.get('abilities'):
                issues.append(f"Pokemon #{pokemon_id} missing abilities")
            if not pokemon.get('stats'):
                issues.append(f"Pokemon #{pokemon_id} missing stats")
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")
        return False
    else:
        print("✓ Database verification passed!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Manage Pokemon Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_db.py --stats                  # Show database statistics
  python manage_db.py --reset --load          # Reset database and load data
  python manage_db.py --load                  # Load data into existing database
  python manage_db.py --clear                 # Clear all data
  python manage_db.py --verify                # Verify database integrity
        """
    )
    
    parser.add_argument('--reset', action='store_true', 
                       help='Reset database (delete and recreate)')
    parser.add_argument('--load', action='store_true', 
                       help='Load Pokemon data from API')
    parser.add_argument('--stats', action='store_true', 
                       help='Show database statistics')
    parser.add_argument('--clear', action='store_true', 
                       help='Clear all data from database')
    parser.add_argument('--verify', action='store_true', 
                       help='Verify database integrity')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        if args.reset:
            db = reset_database()
            if args.load:
                load_pokemon_data(db)
        elif args.load:
            db = PokemonDatabase()
            load_pokemon_data(db)
        elif args.clear:
            clear_database()
        elif args.verify:
            verify_database()
        elif args.stats:
            show_stats()
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 