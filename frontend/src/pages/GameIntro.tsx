import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router";

export function GameIntro() {
  const [playerName, setPlayerName] = useState("");
  const [currentDialogue, setCurrentDialogue] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const dialogues = [
    "Hello there! Welcome to the world of POKéMON!",
    "My name is OAK! People call me the POKéMON PROF!",
    "This world is inhabited by creatures called POKéMON!",
    "Are you ready to test your POKéMON knowledge?",
    "But first, what is your name?",
  ];

  const handleNext = () => {
    if (currentDialogue < dialogues.length - 1) {
      setCurrentDialogue(currentDialogue + 1);
    }
  };

  const handleStartTrivia = async () => {
    if (!playerName.trim()) return;

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/players`, {
        
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: playerName.trim(),
        }),
      });

      // Check if response has content
      const text = await response.text();
      let data;

      try {
        data = text ? JSON.parse(text) : {};
      } catch (parseError) {
        throw new Error(
          `Server returned invalid response: ${response.status} ${response.statusText}`
        );
      }

      if (!response.ok) {
        throw new Error(
          data.error ||
            `Server error: ${response.status} ${response.statusText}`
        );
      }

      // Validate response data
      if (!data.player || !data.player.id) {
        throw new Error("Invalid response from server - missing player data");
      }

      // Store player data in localStorage
      localStorage.setItem("playerName", playerName.trim());
      localStorage.setItem("playerId", data.player.id.toString());

      // Navigate to trivia for the newly created player
      navigate(`/trivia/${data.player.id}`);
    } catch (err) {
      console.error("Player creation error:", err);
      setError(err instanceof Error ? err.message : "Failed to create player");
    } finally {
      setIsLoading(false);
    }
  };

  const isNameInput = currentDialogue === dialogues.length - 1;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="mb-8">
        <img
          src="/professor_oak.png"
          alt="Professor Oak"
          className="w-48 h-48 md:w-64 md:h-64 object-contain"
        />
      </div>

      <Card className="w-full max-w-2xl">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full animate-pulse"></div>
            <span className="text-lg font-bold">PROF. OAK</span>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 rounded min-h-[100px] flex items-center">
            <p className="text-lg md:text-xl font-medium leading-relaxed">
              {dialogues[currentDialogue]}
            </p>
          </div>

          {isNameInput && (
            <div className="space-y-4">
              <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Enter your name..."
                className="w-full p-3 text-lg border-2 focus:outline-none"
                maxLength={12}
                autoFocus
                disabled={isLoading}
              />
              {error && (
                <div className="text-red-500 text-sm bg-red-50 border border-red-200 rounded p-3">
                  {error}
                </div>
              )}
            </div>
          )}

          <div className="flex justify-end gap-3">
            {!isNameInput ? (
              <Button
                onClick={handleNext}
                className=" px-6 py-3 text-lg font-semibold"
              >
                ▶ Next
              </Button>
            ) : (
              <Button
                onClick={handleStartTrivia}
                disabled={!playerName.trim() || isLoading}
                className="w-full py-3 text-lg font-semibold"
              >
                {isLoading ? "Creating Player..." : "Start Adventure! ✨"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2 mt-6">
        {dialogues.map((_, index) => (
          <div
            key={index}
            className={`w-3 h-3 rounded-full ${
              index <= currentDialogue ? "bg-primary" : "bg-primary/30"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
