import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Pokemon } from "@/interfaces/pokemon";

interface PokemonMovesProps {
  pokemon: Pokemon;
  maxDisplayed?: number;
}

export const PokemonMoves = ({ pokemon, maxDisplayed = 20 }: PokemonMovesProps) => {
  const displayedMoves = pokemon.moves.slice(0, maxDisplayed);
  const remainingCount = pokemon.moves.length - maxDisplayed;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Moves ({pokemon.moves.length} total)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-1 max-h-80 overflow-y-auto">
          {displayedMoves.map((move) => (
            <Badge key={move} variant="outline" className="text-xs">
              {move}
            </Badge>
          ))}
          {remainingCount > 0 && (
            <Badge variant="outline" className="text-xs">
              +{remainingCount} more...
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}; 