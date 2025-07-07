import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router";
import type { Pokemon } from "@/interfaces/pokemon";
import { usePokemonList } from "@/hooks/usePokemon";

export function Pokedex() {
  const { pokemonList, loading, error } = usePokemonList();
  const navigate = useNavigate();

  const handlePokemonClick = (pokemonId: number) => {
    navigate(`/pokemon/${pokemonId}`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="text-lg">Loading Pokedex...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold text-red-500 mb-4">
          Error loading Pokedex
        </h1>
        <p>{error.message}</p>
      </div>
    );
  }

  return (
    <>
      <h1 className="text-2xl font-bold text-center pb-6">Pokedex</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {pokemonList.map((pokemon: Pokemon) => (
          <Card 
            key={pokemon.id} 
            className="gap-1 cursor-pointer hover:shadow-lg duration-200 hover:scale-105 transform transition-transform" 
            onClick={() => handlePokemonClick(pokemon.id)}
          >
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
