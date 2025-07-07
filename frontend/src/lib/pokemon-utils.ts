import type { StatName, PokemonTypeVariant, TypeVariant } from "@/interfaces/component-types";
import type { Pokemon } from "@/interfaces/pokemon";

export const statNames: Record<keyof Pokemon['stats'], StatName> = {
  hp: "HP",
  attack: "Attack",
  defense: "Defense",
  "special-attack": "Sp. Attack",
  "special-defense": "Sp. Defense",
  speed: "Speed",
};

const typeMap: Record<string, PokemonTypeVariant> = {
  grass: "grass",
  poison: "poison",
  fire: "fire",
  flying: "flying",
  water: "water",
  bug: "bug",
  normal: "normal",
  electric: "electric",
  ground: "ground",
  fairy: "fairy",
  fighting: "fighting",
  psychic: "psychic",
  rock: "rock",
  steel: "steel",
  ice: "ice",
  ghost: "ghost",
  dragon: "dragon",
};

export const getTypeVariant = (type: string): TypeVariant => {
  return typeMap[type.toLowerCase()] || "outline";
};

export const formatPokemonId = (id: number): string => {
  return id.toString().padStart(3, "0");
};

export const calculateStatPercentage = (value: number, maxValue: number = 255): number => {
  return Math.min((value / maxValue) * 100, 100);
};

export const getPokemonSprite = (pokemon: Pokemon, showShiny: boolean): string => {
  return showShiny && pokemon.shiny_sprite ? pokemon.shiny_sprite : pokemon.sprite;
};

export const getPokemonSpriteAlt = (pokemon: Pokemon, showShiny: boolean): string => {
  return `${pokemon.name} ${showShiny ? "shiny" : "normal"}`;
}; 