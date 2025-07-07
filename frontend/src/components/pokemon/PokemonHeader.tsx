import { Badge } from "@/components/ui/badge";
import type { Pokemon } from "@/interfaces/pokemon";
import { getTypeVariant, formatPokemonId } from "@/lib/pokemon-utils";

interface PokemonHeaderProps {
  pokemon: Pokemon;
}

export const PokemonHeader = ({ pokemon }: PokemonHeaderProps) => {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl lg:text-3xl">
        No{formatPokemonId(pokemon.id)} {pokemon.name.toUpperCase()}
      </h1>

      <div className="flex flex-wrap gap-2">
        {pokemon.types.map((type) => (
          <Badge
            key={type}
            variant={getTypeVariant(type)}
            className="text-base lg:text-lg px-3 py-1"
          >
            {type}
          </Badge>
        ))}
      </div>

      <div className="space-y-2">
        <p className="text-lg lg:text-xl">
          Height: {pokemon.height} m
        </p>
        <p className="text-lg lg:text-xl">
          Weight: {pokemon.weight} kg
        </p>
      </div>
    </div>
  );
}; 