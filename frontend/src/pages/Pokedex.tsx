import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useState } from "react";
import type { Pokemon } from "@/interfaces/pokemon";

const fetchPokemon = async () => {
  const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/pokemon`);
  const data = await response.json();
  console.log(data);
  return data;
};

export function Pokedex() {
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);

  useEffect(() => {
    const fetchPokemonData = async () => {
      const pokemon = await fetchPokemon();
      setPokemon(pokemon);
    };
    fetchPokemonData();
  }, []);

  return (
    <>
      <h1 className="text-2xl font-bold text-center pb-6">Pokedex</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {pokemon.map((pokemon: Pokemon) => (
          <Card key={pokemon.id} className="gap-1 -full">
            <CardHeader >
              <CardTitle className="text-center text-2xl font-bold">
                {pokemon.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <img src={pokemon.sprite} alt={pokemon.name} />
            </CardContent>
            <CardFooter className="text-lg font-bold">
              No.{pokemon.id}
            </CardFooter>
          </Card>
        ))}
      </div>
    </>
  );
}
