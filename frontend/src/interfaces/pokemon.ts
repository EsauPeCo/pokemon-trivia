export interface PokemonStats {
  attack: number;
  defense: number;
  hp: number;
  "special-attack": number;
  "special-defense": number;
  speed: number;
}

export interface EvolutionDetails {
  min_level?: number;
  trigger: string;
}

export interface EvolutionChain {
  name: string;
  evolution_details?: EvolutionDetails;
  evolves_to: EvolutionChain[];
}

export interface Pokemon {
  id: number;
  name: string;
  abilities: string[];
  base_experience: number;
  height: number;
  weight: number;
  moves: string[];
  sprite: string;
  shiny_sprite: string;
  stats: PokemonStats;
  types: string[];
  flavor_text?: string;
  habitat?: string;
  shape?: string;
  evolution_chain?: EvolutionChain;
} 