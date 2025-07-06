import { Button } from "@/components/ui/button";
import { Link } from "react-router";

function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <img
        src="/International_Pokémon_logo.svg.png"
        alt="Pokemon Logo"
        className="w-120 h-auto mb-6"
      />
      <h1 className="text-center text-4xl font-bold">Pokemon-Trivia</h1>
      <div className="flex items-center justify-center gap-4">
        <Link to="/pokedex">
          <Button className="mt-4 cursor-pointer">Pokedex</Button>
        </Link>
        <Button className="mt-4 cursor-pointer">Trivia</Button>
      </div>
    </div>
  );
}

export default App;
