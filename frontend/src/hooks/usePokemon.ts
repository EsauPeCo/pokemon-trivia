import { useState, useEffect } from "react";
import type { Pokemon } from "@/interfaces/pokemon";
import type { PokemonError } from "@/interfaces/component-types";

//cache for pokemon list
let pokemonListCache: Pokemon[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

const fetchPokemonById = async (id: string): Promise<Pokemon> => {
  const response = await fetch(
    `${import.meta.env.VITE_BACKEND_API}/pokemon/${id}`
  );
  if (!response.ok) {
    throw new Error("Pokemon not found");
  }
  const data: Pokemon = await response.json();
  return data;
};

const fetchAllPokemon = async (): Promise<Pokemon[]> => {
  const now = Date.now();
  if (pokemonListCache && (now - cacheTimestamp) < CACHE_DURATION) {
    return pokemonListCache;
  }

  const response = await fetch(
    `${import.meta.env.VITE_BACKEND_API}/pokemon`
  );
  if (!response.ok) {
    throw new Error("Failed to fetch Pokemon list");
  }
  const data: Pokemon[] = await response.json();
  
  pokemonListCache = data;
  cacheTimestamp = now;
  
  return data;
};

export interface UsePokemonReturn {
  pokemon: Pokemon | null;
  loading: boolean;
  error: PokemonError | null;
}

export interface UsePokemonListReturn {
  pokemonList: Pokemon[];
  loading: boolean;
  error: PokemonError | null;
}

export const usePokemon = (id: string | undefined): UsePokemonReturn => {
  const [pokemon, setPokemon] = useState<Pokemon | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<PokemonError | null>(null);

  useEffect(() => {
    const fetchPokemonData = async (): Promise<void> => {
      if (!id) return;

      try {
        setLoading(true);
        setError(null);
        const pokemonData = await fetchPokemonById(id);
        setPokemon(pokemonData);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An error occurred";
        setError({ message: errorMessage });
      } finally {
        setLoading(false);
      }
    };

    fetchPokemonData();
  }, [id]);

  return { pokemon, loading, error };
};

export const usePokemonList = (): UsePokemonListReturn => {
  const [pokemonList, setPokemonList] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<PokemonError | null>(null);

  useEffect(() => {
    const fetchPokemonListData = async (): Promise<void> => {
      try {
        setLoading(false);
        if (pokemonListCache) {
          setPokemonList(pokemonListCache);
        } else {
          setLoading(true);
        }
        
        setError(null);
        const pokemonListData = await fetchAllPokemon();
        setPokemonList(pokemonListData);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An error occurred";
        setError({ message: errorMessage });
      } finally {
        setLoading(false);
      }
    };

    fetchPokemonListData();
  }, []);

  return { pokemonList, loading, error };
}; 