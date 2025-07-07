import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Pokemon } from "@/interfaces/pokemon";
import { statNames, calculateStatPercentage } from "@/lib/pokemon-utils";

interface PokemonStatsProps {
  pokemon: Pokemon;
}

export const PokemonStats = ({ pokemon }: PokemonStatsProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Base Stats</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {Object.entries(pokemon.stats).map(([statKey, value]) => (
          <div key={statKey} className="space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">
                {statNames[statKey as keyof typeof pokemon.stats] || statKey}:
              </span>
              <span className="font-bold">{value}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${calculateStatPercentage(value)}%` }}
              ></div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}; 