import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { useParams, useNavigate } from "react-router";
import type { ReactElement } from "react";
import { usePokemon, usePokemonList } from "@/hooks/usePokemon";
import {
  PokemonHeader,
  PokemonImage,
  PokemonStats,
  PokemonMoves,
  PokemonAdditionalInfo,
} from "@/components/pokemon";

export function PokemonDetail(): ReactElement {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { pokemon, loading, error } = usePokemon(id);
  const { pokemonList } = usePokemonList();
  const [showShiny, setShowShiny] = useState<boolean>(false);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (error || !pokemon) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold text-red-500 mb-4">
          Pokemon Not Found
        </h1>
        <button
          onClick={() => navigate("/pokedex")}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Back to Pokedex
        </button>
      </div>
    );
  }

  const handleBackClick = (): void => {
    navigate("/pokedex");
  };

  const handleShinyToggle = (checked: boolean): void => {
    setShowShiny(checked);
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center mb-6">
        <button
          onClick={handleBackClick}
          className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
        >
          ← Back to Pokedex
        </button>
      </div>

      <Card className="mb-6">
        <CardContent className="p-6 lg:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div className="order-2 lg:order-1">
              <PokemonHeader pokemon={pokemon} />
            </div>
            <div className="order-1 lg:order-2">
              <PokemonImage
                pokemon={pokemon}
                showShiny={showShiny}
                onShinyToggle={handleShinyToggle}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {pokemon.flavor_text && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="italic">{pokemon.flavor_text}</p>
          </CardContent>
        </Card>
      )}

      <PokemonAdditionalInfo pokemon={pokemon} pokemonList={pokemonList} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PokemonStats pokemon={pokemon} />
        <PokemonMoves pokemon={pokemon} />
      </div>
    </div>
  );
}
