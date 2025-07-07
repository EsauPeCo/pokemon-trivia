import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Pokemon } from "@/interfaces/pokemon";
import type { EvolutionChainComponentProps } from "@/interfaces/component-types";

const EvolutionChainComponent = ({
  evolutionData,
  pokemonList,
}: EvolutionChainComponentProps) => {
  if (!evolutionData) return null;

  const pokemonLookup =
    pokemonList?.reduce((acc, p) => {
      acc[p.name.toLowerCase()] = p;
      return acc;
    }, {} as Record<string, Pokemon>) || {};

  const renderEvolution = (evolution: any) => {
    const pokemonData = pokemonLookup[evolution.name.toLowerCase()];

    return (
      <div key={evolution.name} className="flex items-center space-x-4">
        <div className="text-center min-w-36">
          {pokemonData ? (
            <img
              src={pokemonData.sprite}
              alt={evolution.name}
              className="w-32 h-32 mx-auto mb-2 object-contain hover:scale-110 transition-transform duration-200"
            />
          ) : (
            <div className="w-32 h-32 mx-auto mb-2 bg-gray-100 rounded-lg flex items-center justify-center">
              <span className="text-xs text-gray-400">No Image</span>
            </div>
          )}
          <Badge variant="outline" className="mb-2 text-xs">
            {evolution.name}
          </Badge>
        </div>
        {evolution.evolves_to && evolution.evolves_to.length > 0 && (
          <>
            <div className="flex flex-col items-center px-2">
              <div className="text-2xl text-gray-400">→</div>
              {evolution.evolves_to[0].evolution_details && (
                <div className="text-xs text-gray-500 mt-1 text-center">
                  {evolution.evolves_to[0].evolution_details.trigger ===
                    "Level-Up" &&
                    evolution.evolves_to[0].evolution_details.min_level && (
                      <span>
                        Lv.{" "}
                        {evolution.evolves_to[0].evolution_details.min_level}
                      </span>
                    )}
                  {evolution.evolves_to[0].evolution_details.trigger !==
                    "Level-Up" && (
                    <span>
                      {evolution.evolves_to[0].evolution_details.trigger}
                    </span>
                  )}
                </div>
              )}
            </div>
            {evolution.evolves_to.map((nextEvolution: any) =>
              renderEvolution(nextEvolution)
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-wrap items-center justify-center gap-2 p-4rounded-lg">
      {renderEvolution(evolutionData)}
    </div>
  );
};

interface PokemonAdditionalInfoProps {
  pokemon: Pokemon;
  pokemonList?: Pokemon[];
}

export const PokemonAdditionalInfo = ({
  pokemon,
  pokemonList,
}: PokemonAdditionalInfoProps) => {
  const infoItems = [
    {
      label: "Base Experience",
      value: pokemon.base_experience?.toString() || "N/A",
    },
    ...(pokemon.habitat
      ? [
          {
            label: "Habitat",
            value: pokemon.habitat,
          },
        ]
      : []),
    ...(pokemon.shape
      ? [
          {
            label: "Shape",
            value: pokemon.shape,
          },
        ]
      : []),
  ];

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Additional Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          {infoItems.map((item, index) => (
            <div
              key={index}
              className="flex justify-between items-center py-2 border-b border-gray-100"
            >
              <span className="font-medium">{item.label}:</span>
              <span className="font-semibold">{item.value}</span>
            </div>
          ))}
        </div>

        <div className="py-2 border-b border-gray-100">
          <div className="flex justify-between items-start mb-3">
            <span className="font-medium">Abilities:</span>
            <div className="flex flex-wrap gap-2 max-w-xs justify-end">
              {pokemon.abilities.map((ability) => (
                <Badge key={ability} variant="secondary">
                  {ability}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {pokemon.evolution_chain && (
          <div>
            <div className="mb-3">
              <span className="font-medium">Evolution Chain:</span>
            </div>
            <div className="mt-2">
              <EvolutionChainComponent
                evolutionData={pokemon.evolution_chain}
                pokemonList={pokemonList}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
