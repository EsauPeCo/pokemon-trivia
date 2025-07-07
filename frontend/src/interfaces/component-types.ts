import type { badgeVariants } from "@/components/ui/badge";
import type { VariantProps } from "class-variance-authority";

export type BadgeVariant = VariantProps<typeof badgeVariants>['variant'];

export type PokemonTypeVariant = 
  | "grass"
  | "poison"
  | "fire"
  | "flying"
  | "water"
  | "bug"
  | "normal"
  | "electric"
  | "ground"
  | "fairy"
  | "fighting"
  | "psychic"
  | "rock"
  | "steel"
  | "ice"
  | "ghost"
  | "dragon";

export type TypeVariant = PokemonTypeVariant | "outline" | "default" | "secondary" | "destructive";

export type StatName =
  | "HP"
  | "Attack"
  | "Defense"
  | "Sp. Attack"
  | "Sp. Defense"
  | "Speed";

export interface PokemonError {
  message: string;
  code?: string;
}

export interface EvolutionChainComponentProps {
  evolutionData: import("./pokemon").EvolutionChain;
  pokemonList?: import("./pokemon").Pokemon[];
}
