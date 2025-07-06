import FlyingItems from "@/components/FlyingItems";
import { Link, useNavigate } from "react-router";
import { useEffect } from "react";

function App() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === "Enter") {
        navigate("/menu");
      }
    };

    window.addEventListener("keydown", handleKeyPress);

    return () => {
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, [navigate]);

  return (
    <div className="h-screen flex items-center justify-center pixelated bg-background">
      <div className="relative aspect-[10/6] h-full max-h-screen p-4 md:p-10">
        {/* Hide flying items on mobile */}
        <div className="hidden md:block">
          <FlyingItems />
        </div>

        {/* Background  layout*/}
        <img
          src="/oak-lab.jpg"
          alt="Oak Lab Background"
          className="absolute inset-0 w-full h-full object-cover object-center brightness-70"
        />

        {/* Hide decorative background strips on mobile */}
        <div className="hidden md:block">
          <div className="absolute left-0 right-0 top-0 h-15 bg-[#d5c6a1]"></div>
          <div className="absolute left-0 right-0 top-15 h-30 bg-background"></div>
          <div className="absolute left-0 right-0 bottom-0 h-13 bg-[#7a6b4a]"></div>
          <div className="absolute left-0 right-0 bottom-13 h-60 bg-background"></div>
        </div>

        {/* Simplified background for mobile */}
        <div className="md:hidden absolute left-0 right-0 bottom-0 h-20 bg-background/80"></div>

        <Link
          to="/Menu"
          className="absolute cursor-pointer left-4 md:left-10 right-4 md:right-10 bottom-2 md:bottom-13 h-16 md:h-60 flex items-center justify-center text-xl md:text-4xl font-semibold metallic-text md:mr-80 z-10"
        >
          PRESS START
        </Link>

        {/* Content Layout */}
        <div className="relative h-full flex">
          <div className="flex-1 flex flex-col items-center justify-center md:justify-between">
            <div className="flex flex-col items-center -mt-10 md:-mt-6">
              <div className="shine-effect">
                <img
                  src="/International_Pokémon_logo.svg.png"
                  alt="Pokemon Logo"
                  className="w-64 md:w-220 h-auto"
                />
              </div>
              <img
                src="/Trivia.svg"
                alt="Trivia"
                className="w-auto h-28 md:h-85 -mt-8 md:-mt-22"
              />
            </div>
          </div>

          {/* Hide Professor Oak on mobile */}
          <div className="hidden md:flex w-80 relative items-end justify-center mb-5">
            <img
              src="/professor_oak.png"
              alt="Professor Oak"
              className="w-full h-auto max-w-md"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
