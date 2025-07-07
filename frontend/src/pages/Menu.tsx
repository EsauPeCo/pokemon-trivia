import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router";

interface Player {
  id: number;
  name: string;
  created_at: string;
}

interface GameSession {
  id: number;
  player_id: number;
  start_time: string;
  end_time: string | null;
  total_questions: number;
  correct_answers: number;
  score: number;
  is_perfect_score: boolean;
  difficulty: string | null;
  session_type: string;
  metadata: any;
  created_at: string;
  player_name: string;
}

export function Menu() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedPlayerSessions, setSelectedPlayerSessions] = useState<GameSession[] | null>(null);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [selectedPlayerName, setSelectedPlayerName] = useState("");

  useEffect(() => {
    fetchPlayers();
  }, []);

  const fetchPlayers = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/players`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch players: ${response.status}`);
      }

      const data = await response.json();
      setPlayers(data.players || []);
    } catch (err) {
      console.error("Error fetching players:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch players");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPlayerSessions = async (playerId: number, playerName: string) => {
    try {
      setLoadingSessions(true);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/players/${playerId}/sessions`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch sessions: ${response.status}`);
      }

      const data = await response.json();
      setSelectedPlayerSessions(data.sessions || []);
      setSelectedPlayerName(playerName);
    } catch (err) {
      console.error("Error fetching sessions:", err);
      setSelectedPlayerSessions([]);
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleViewSessions = (e: React.MouseEvent, playerId: number, playerName: string) => {
    e.preventDefault();
    e.stopPropagation();
    fetchPlayerSessions(playerId, playerName);
  };

  const closeSessions = () => {
    setSelectedPlayerSessions(null);
    setSelectedPlayerName("");
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (startTime: string, endTime: string | null) => {
    if (!endTime) return "In progress";
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end.getTime() - start.getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const canCreateNewPlayer = players.length < 3;

  return (
    <div className="flex flex-col items-center justify-start h-full px-5 gap-4">
      {canCreateNewPlayer && (
        <Link className="w-full" to="/game-intro">
          <Card className="w-full">
            <CardHeader className="flex flex-col justify-center">
              <CardTitle className="text-2xl sm:text-4xl lg:text-7xl font-light">
                NEW GAME
              </CardTitle>
            </CardHeader>
          </Card>
        </Link>
      )}

      {isLoading ? (
        <Card className="w-full">
          <CardContent className="p-6">
            <p className="text-center">Loading players...</p>
          </CardContent>
        </Card>
      ) : error ? (
        <Card className="w-full">
          <CardContent className="p-6">
            <p className="text-center text-red-500">Error: {error}</p>
          </CardContent>
        </Card>
      ) : players.length > 0 ? (
        <div className="w-full space-y-2">
          <h2 className="text-xl font-semibold text-center mb-4">Existing Players</h2>
          {players.map((player) => (
            <div key={player.id} className="relative">
              <Link className="w-full block" to={`/trivia/${player.id}`}>
                <Card className="w-full cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  <CardHeader className="py-3 pr-20">
                    <CardTitle className="text-2xl sm:text-4xl lg:text-7xl font-light">
                      {player.name}
                    </CardTitle>
                  </CardHeader>
                </Card>
              </Link>
              <Button
                variant="outline"
                size="sm"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 z-10"
                onClick={(e) => handleViewSessions(e, player.id, player.name)}
              >
                Sessions
              </Button>
            </div>
          ))}
          {!canCreateNewPlayer && (
            <Card className="w-full">
              <CardContent className="p-4">
                <p className="text-center text-amber-600 font-medium">
                  Player limit reached (3/3)
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      ) : null}

      {/* Sessions Modal */}
      {selectedPlayerSessions !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-2xl font-bold">
                {selectedPlayerName}'s Game Sessions
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={closeSessions}>
                ✕
              </Button>
            </CardHeader>
            <CardContent className="overflow-y-auto max-h-[60vh]">
              {loadingSessions ? (
                <p className="text-center py-4">Loading sessions...</p>
              ) : selectedPlayerSessions.length === 0 ? (
                <p className="text-center py-4 text-gray-500">No game sessions found</p>
              ) : (
                <div className="space-y-3">
                  {selectedPlayerSessions.map((session) => (
                    <Card key={session.id} className="bg-gray-50 dark:bg-gray-800">
                      <CardContent className="p-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="font-semibold">Session #{session.id}</p>
                            <p className="text-gray-600 dark:text-gray-400">
                              {formatDate(session.start_time)}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold">
                              {session.correct_answers}/{session.total_questions} correct
                            </p>
                            <p className="text-gray-600 dark:text-gray-400">
                              Score: {session.score}
                            </p>
                          </div>
                          <div>
                            <p><span className="font-medium">Type:</span> {session.session_type}</p>
                            {session.difficulty && (
                              <p><span className="font-medium">Difficulty:</span> {session.difficulty}</p>
                            )}
                          </div>
                          <div className="text-right">
                            <p><span className="font-medium">Duration:</span> {formatDuration(session.start_time, session.end_time)}</p>
                            {session.is_perfect_score && (
                              <p className="text-green-600 font-semibold">Perfect Score! 🏆</p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      <Link className="w-full" to="/pokedex">
        <Card className="w-full">
          <CardHeader className="flex flex-col justify-center">
            <CardTitle className="text-2xl sm:text-4xl lg:text-7xl font-light">
              POKéDEX
            </CardTitle>
          </CardHeader>
        </Card>
      </Link>
    </div>
  );
}
