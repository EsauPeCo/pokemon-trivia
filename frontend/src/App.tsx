import { Button } from "@/components/ui/button";

const fetchPokemon = async () => {
  const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/pokemon`);
  const data = await response.json();
  console.log(data);
};

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-center text-4xl font-bold">Pokemon-Trivia</h1>
      <Button onClick={fetchPokemon} className="mt-4 cursor-pointer">
        Start
      </Button>
    </div>
  );
}

export default App;
