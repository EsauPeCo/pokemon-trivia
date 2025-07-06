import requests


# Helper function to parse evolution chain data
def parse_evolution_chain(chain_data):
    """Parse evolution chain data recursively"""

    def parse_evolution_details(evolution_details):
        """Parse evolution trigger details - simplified for Gen 1 triggers"""
        if not evolution_details:
            return None

        detail = evolution_details[0]  # Take the first evolution detail
        trigger_name = detail["trigger"]["name"] if detail.get("trigger") else None

        trigger_info = {
            "trigger": trigger_name.title() if trigger_name else None,
        }

        # Add specific trigger details based on known Gen 1 triggers
        if trigger_name == "level-up":
            if detail.get("min_level"):
                trigger_info["min_level"] = detail["min_level"]

        elif trigger_name == "use-item":
            if detail.get("item"):
                trigger_info["item"] = detail["item"]["name"].title()

        elif trigger_name == "trade":
            if detail.get("held_item"):
                trigger_info["held_item"] = detail["held_item"]["name"].title()
            if detail.get("trade_species"):
                trigger_info["trade_species"] = detail["trade_species"]["name"].title()

        elif trigger_name == "other":
            # Handle any special conditions for 'other' trigger
            if detail.get("min_level"):
                trigger_info["min_level"] = detail["min_level"]
            if detail.get("min_happiness"):
                trigger_info["min_happiness"] = detail["min_happiness"]

        return trigger_info

    def parse_chain_node(node):
        """Recursively parse evolution chain node"""
        pokemon_name = node["species"]["name"].title()

        chain_node = {"name": pokemon_name}

        # Only add evolution_details if they exist (not for base pokemon)
        evolution_details = parse_evolution_details(node.get("evolution_details"))
        if evolution_details:
            chain_node["evolution_details"] = evolution_details

        # Parse evolves_to recursively, only if there are evolutions
        if node.get("evolves_to"):
            evolutions = [
                parse_chain_node(evolution) for evolution in node["evolves_to"]
            ]
            if evolutions:
                chain_node["evolves_to"] = evolutions

        return chain_node

    return parse_chain_node(chain_data)


# Function to fetch and clean Pokémon data from PokeAPI
def fetch_pokemon_data():
    """Fetch the first 151 Pokémon from PokeAPI"""
    pokemons = []

    try:
        # Fetch the first 151 Pokémon (IDs 1-151)
        for pokemon_id in range(1, 152):
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
            if response.status_code == 200:
                pokemon_data = response.json()

                # Fetch species data for flavor text, habitat, shape, and evolution chain
                species_response = requests.get(
                    f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
                )
                flavor_text = "No description available."
                habitat = None
                shape = None
                evolution_chain = None

                if species_response.status_code == 200:
                    species_data = species_response.json()

                    # Find English flavor text entries
                    english_entries = [
                        entry
                        for entry in species_data.get("flavor_text_entries", [])
                        if entry["language"]["name"] == "en"
                    ]
                    if english_entries:
                        # Use the first English entry (usually from the most recent game)
                        flavor_text = (
                            english_entries[0]["flavor_text"]
                            .replace("\n", " ")
                            .replace("\f", " ")
                        )

                    if species_data.get("habitat") and species_data["habitat"]:
                        habitat = species_data["habitat"]["name"].title()

                    if species_data.get("shape") and species_data["shape"]:
                        shape = species_data["shape"]["name"].title()

                    if (
                        species_data.get("evolution_chain")
                        and species_data["evolution_chain"]["url"]
                    ):
                        evolution_url = species_data["evolution_chain"]["url"]
                        evolution_response = requests.get(evolution_url)

                        if evolution_response.status_code == 200:
                            evolution_data = evolution_response.json()
                            evolution_chain = parse_evolution_chain(
                                evolution_data["chain"]
                            )

                # Extract relevant information
                pokemon = {
                    "id": pokemon_data["id"],
                    "name": pokemon_data["name"].title(),
                    "types": [
                        type_info["type"]["name"].title()
                        for type_info in pokemon_data["types"]
                    ],
                    "height": pokemon_data["height"] / 10,  # Convert to meters
                    "weight": pokemon_data["weight"] / 10,  # Convert to kg
                    "sprite": pokemon_data["sprites"]["other"]["official-artwork"][
                        "front_default"
                    ],
                    "shiny_sprite": pokemon_data["sprites"]["other"][
                        "official-artwork"
                    ]["front_shiny"],
                    "abilities": [
                        ability["ability"]["name"].title()
                        for ability in pokemon_data["abilities"]
                    ],
                    "base_experience": pokemon_data["base_experience"],
                    "moves": [
                        move["move"]["name"].title() for move in pokemon_data["moves"]
                    ],
                    "stats": {
                        stat["stat"]["name"]: stat["base_stat"]
                        for stat in pokemon_data["stats"]
                    },
                    "flavor_text": flavor_text,
                    "habitat": habitat,
                    "shape": shape,
                    "evolution_chain": evolution_chain,
                }
                pokemons.append(pokemon)
                print(f"Fetched {pokemon['name']} (ID: {pokemon['id']})")
            else:
                print(f"Failed to fetch Pokémon with ID {pokemon_id}")

    except Exception as e:
        print(f"Error fetching Pokémon data: {e}")
        return []

    return pokemons
