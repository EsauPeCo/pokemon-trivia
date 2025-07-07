import { Switch } from "@/components/ui/switch";
import type { Pokemon } from "@/interfaces/pokemon";
import { getPokemonSprite, getPokemonSpriteAlt } from "@/lib/pokemon-utils";

interface PokemonImageProps {
  pokemon: Pokemon;
  showShiny: boolean;
  onShinyToggle: (checked: boolean) => void;
}

export const PokemonImage = ({ pokemon, showShiny, onShinyToggle }: PokemonImageProps) => {
  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="text-center">
        <img
          src={getPokemonSprite(pokemon, showShiny)}
          alt={getPokemonSpriteAlt(pokemon, showShiny)}
          className="w-48 h-48 lg:w-64 lg:h-64 mx-auto"
        />
      </div>
      
      {pokemon.shiny_sprite && (
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium">Normal</span>
          <Switch checked={showShiny} onCheckedChange={onShinyToggle} />
          <span className="text-sm font-medium">Shiny</span>
        </div>
      )}
    </div>
  );
}; 