import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useParams } from "react-router";

interface TriviaQuestion {
  question: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  explanation: string;
  difficulty: string;
  question_type?: string;
  category?: string;
  pokemon_name: string;
  pokemon_id: number;
  generated_at?: string;
  id?: number;
}

interface Pokemon {
  id: number;
  name: string;
  types: string[];
  sprite_url?: string;
}

interface QuestionRating {
  question_id: number;
  action: 'like' | 'dislike';
}

interface GameSession {
  id: number;
  player_id: string;
  session_type: string;
  difficulty?: string;
  created_at: string;
}

export const Trivia = () => {
  const { playerId } = useParams<{ playerId: string }>();
  const [questions, setQuestions] = useState<TriviaQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [sessionPokemon, setSessionPokemon] = useState<Pokemon | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState<boolean>(false);
  const [timeLeft, setTimeLeft] = useState<number>(15);
  const [timerActive, setTimerActive] = useState<boolean>(false);
  const [showIntermediateCard, setShowIntermediateCard] =
    useState<boolean>(false);
  const [questionsAnswered, setQuestionsAnswered] = useState<number>(0);
  const [correctAnswers, setCorrectAnswers] = useState<number>(0);
  const [showFinalResults, setShowFinalResults] = useState<boolean>(false);
  const [playerName, setPlayerName] = useState<string>("");
  
  const [currentSession, setCurrentSession] = useState<GameSession | null>(null);
  const [questionRatings, setQuestionRatings] = useState<QuestionRating[]>([]);
  const [currentQuestionRated, setCurrentQuestionRated] = useState<boolean>(false);
  const [savingResults, setSavingResults] = useState<boolean>(false);
  const [sessionInitialized, setSessionInitialized] = useState<boolean>(false);

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    if (playerId) {
      fetchPlayerInfo();
    }
  }, [playerId]);

  const fetchPlayerInfo = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/players/${playerId}`);
      if (response.ok) {
        const player = await response.json();
        setPlayerName(player.name);
      }
    } catch (err) {
      console.error("Error fetching player info:", err);
    }
  };

  const createGameSession = async (pokemon?: Pokemon): Promise<GameSession | null> => {
    if (!playerId) return null;
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_id: playerId,
          session_type: "random",
          difficulty: "mixed",
          metadata: {
            pokemon_name: pokemon?.name || sessionPokemon?.name,
            pokemon_id: pokemon?.id || sessionPokemon?.id
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create game session: ${response.status}`);
      }

      const data = await response.json();
      return data.session;
    } catch (err) {
      console.error("Error creating game session:", err);
      return null;
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (timerActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setTimerActive(false);
            if (!showResult) {
              setShowResult(true);
              setQuestionsAnswered((prevQ) => prevQ + 1);
            }
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [timerActive, timeLeft, showResult]);

  useEffect(() => {
    if (showResult && !showIntermediateCard) {
      const timeout = setTimeout(() => {
        setShowIntermediateCard(true);
      }, 2000);

      return () => clearTimeout(timeout);
    }
  }, [showResult, showIntermediateCard]);

  const fetchRandomPokemon = async (): Promise<Pokemon> => {
    const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/pokemon`);
    if (!response.ok) {
      throw new Error(`Failed to fetch Pokemon list: ${response.status}`);
    }

    const pokemonList: Pokemon[] = await response.json();
    const randomIndex = Math.floor(Math.random() * pokemonList.length);
    return pokemonList[randomIndex];
  };

  const generateQuestionsForPokemon = async (
    pokemon: Pokemon
  ): Promise<TriviaQuestion[]> => {
    // Configuration options for variety
    const difficulties = ["easy", "medium", "hard"];
    const questionTypes = [
      "general",
      "stats", 
      "moves",
      "evolution",
      "basic_info",
    ];

    // Randomly select configuration for all 5 questions
    const selectedDifficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
    const selectedQuestionType = questionTypes[Math.floor(Math.random() * questionTypes.length)];

    const response = await fetch(
      `${import.meta.env.VITE_BACKEND_API}/trivia/generate-five`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pokemon_id: pokemon.id,
          difficulty: selectedDifficulty,
          question_type: selectedQuestionType,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to generate questions: ${response.status}`
      );
    }

    const data = await response.json();
    
    // Extract questions from the response
    const questions: TriviaQuestion[] = data.questions || [];
    
    if (questions.length !== 5) {
      throw new Error(`Expected 5 questions, but received ${questions.length}`);
    }

    console.log(`Generated 5 ${selectedDifficulty} ${selectedQuestionType} questions for ${pokemon.name}`);
    
    return questions;
  };

  const startNewTriviaSession = async () => {
    try {
      setLoading(true);
      setError(null);
      setQuestions([]);
      setCurrentQuestionIndex(0);
      setSelectedAnswer(null);
      setShowResult(false);
      setShowIntermediateCard(false);
      setTimeLeft(15);
      setTimerActive(false);
      setQuestionsAnswered(0);
      setCorrectAnswers(0);
      setShowFinalResults(false);
      setCurrentSession(null);
      setQuestionRatings([]);
      setCurrentQuestionRated(false);
      setSessionInitialized(true);

      const pokemon = await fetchRandomPokemon();
      setSessionPokemon(pokemon);

      const generatedQuestions = await generateQuestionsForPokemon(pokemon);
      setQuestions(generatedQuestions);

      // Create game session
      const session = await createGameSession(pokemon);
      if (session) {
        setCurrentSession(session);
      }

      setTimerActive(true);

      console.log(
        `Started trivia session with ${pokemon.name}:`,
        generatedQuestions
      );
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
      console.error("Error starting trivia session:", errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answer: string) => {
    if (showResult || !timerActive) return;

    setSelectedAnswer(answer);
    setShowResult(true);
    setTimerActive(false);

    setQuestionsAnswered((prev) => prev + 1);
    if (answer === currentQuestion?.correct_answer) {
      setCorrectAnswers((prev) => prev + 1);
    }
  };

  const getPokemonSpriteUrl = (pokemonId: number): string => {
    return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${pokemonId}.png`;
  };

  const getOptionVariant = (optionKey: string) => {
    if (!showResult) return "outline";

    if (optionKey === currentQuestion?.correct_answer) {
      return "default";
    }

    if (
      optionKey === selectedAnswer &&
      optionKey !== currentQuestion?.correct_answer
    ) {
      return "destructive";
    }

    return "secondary";
  };

  const getOptionClasses = (optionKey: string) => {
    if (!showResult) {
      return "hover:scale-[0.98] transition-all duration-200";
    }

    if (optionKey === currentQuestion?.correct_answer) {
      return "bg-green-500 hover:bg-green-500 text-white border-green-600";
    }

    if (
      optionKey === selectedAnswer &&
      optionKey !== currentQuestion?.correct_answer
    ) {
      return "";
    }

    return "opacity-60";
  };

  const handleLike = () => {
    if (!currentQuestion?.id || currentQuestionRated) return;
    
    setQuestionRatings(prev => [
      ...prev,
      { question_id: currentQuestion.id!, action: 'like' }
    ]);
    setCurrentQuestionRated(true);
    console.log("Question liked:", currentQuestion?.question);
  };

  const handleDislike = () => {
    if (!currentQuestion?.id || currentQuestionRated) return;
    
    setQuestionRatings(prev => [
      ...prev,
      { question_id: currentQuestion.id!, action: 'dislike' }
    ]);
    setCurrentQuestionRated(true);
    console.log("Question disliked:", currentQuestion?.question);
  };

  const goToNextQuestion = async () => {
    if (questionsAnswered >= 5) {
      // Save session results before showing final results
      await saveSessionResults();
      setShowFinalResults(true);
    } else {
      setCurrentQuestionIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setShowResult(false);
      setShowIntermediateCard(false);
      setTimeLeft(15);
      setTimerActive(true);
      setCurrentQuestionRated(false); // Reset rating state for new question
    }
  };

  const startNewGame = () => {
    setSessionInitialized(false);
    startNewTriviaSession();
  };

  useEffect(() => {
    if (!sessionInitialized && playerId) {
      startNewTriviaSession();
    }
  }, [sessionInitialized, playerId]);

  const saveQuestionRatings = async () => {
    if (questionRatings.length === 0) return;

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/trivia/questions/rating`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          updates: questionRatings
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save question ratings: ${response.status}`);
      }

      console.log("Question ratings saved successfully");
    } catch (err) {
      console.error("Error saving question ratings:", err);
    }
  };

  const saveSessionResults = async () => {
    if (!currentSession) return;

    try {
      setSavingResults(true);
      
      // Save question ratings first
      await saveQuestionRatings();

      // Update the session with results
      const response = await fetch(`${import.meta.env.VITE_BACKEND_API}/sessions/${currentSession.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          end_session: true,
          total_questions: 5,
          correct_answers: correctAnswers,
          score: Math.round((correctAnswers / 5) * 100),
          metadata: {
            pokemon_name: sessionPokemon?.name,
            pokemon_id: sessionPokemon?.id,
            ratings_count: questionRatings.length
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save session results: ${response.status}`);
      }

      const updatedSession = await response.json();
      console.log("Session results saved successfully:", updatedSession);

    } catch (err) {
      console.error("Error saving session results:", err);
    } finally {
      setSavingResults(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-xl font-semibold">
                {sessionPokemon
                  ? `Generating questions for ${sessionPokemon.name}...`
                  : "Preparing your trivia session..."}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-4">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-destructive">
              Error
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-muted-foreground">{error}</p>
            <Button onClick={startNewTriviaSession} variant="destructive">
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!currentQuestion) return null;

  if (showFinalResults) {
    const percentage = Math.round((correctAnswers / 5) * 100);
    const getScoreMessage = () => {
      if (percentage >= 80) return "🏆 Outstanding Pokémon Master!";
      if (percentage >= 60) return "⚡ Great Pokémon Trainer!";
      if (percentage >= 40) return "🎯 Good Pokémon Knowledge!";
      return "📚 Keep studying, future trainer!";
    };

    return (
      <div className="flex items-center justify-center p-4">
        <Card className="max-w-lg w-full">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold">
              {playerName ? `${playerName}'s Trivia Complete!` : "Trivia Complete!"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-center">
            {sessionPokemon && (
              <div className="space-y-2">
                <div className="w-24 h-24 mx-auto">
                  <img
                    src={getPokemonSpriteUrl(sessionPokemon.id)}
                    alt={sessionPokemon.name}
                    className="w-full h-full object-contain"
                  />
                </div>
                <p className="text-lg font-semibold">
                  You completed the{" "}
                  <span className="text-primary capitalize">
                    {sessionPokemon.name}
                  </span>{" "}
                  trivia!
                </p>
              </div>
            )}

            <div className="relative w-32 h-32 mx-auto">
              <div className="w-full h-full rounded-full border-8 border-muted flex items-center justify-center relative overflow-hidden">
                <div
                  className="absolute inset-0 rounded-full border-8 border-primary"
                  style={{
                    clipPath: `polygon(50% 50%, 50% 0%, ${
                      50 +
                      50 * Math.cos(((percentage * 3.6 - 90) * Math.PI) / 180)
                    }% ${
                      50 -
                      50 * Math.sin(((percentage * 3.6 - 90) * Math.PI) / 180)
                    }%, 50% 50%)`,
                  }}
                />
                <div className="text-3xl font-bold z-10 bg-background rounded-full w-24 h-24 flex items-center justify-center">
                  {percentage}%
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-xl font-semibold">{getScoreMessage()}</h3>
              <p className="text-lg">
                You got{" "}
                <span className="font-bold text-primary">{correctAnswers}</span>{" "}
                out of <span className="font-bold">5</span> questions correct!
              </p>
              {questionRatings.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  You rated {questionRatings.length} question{questionRatings.length !== 1 ? 's' : ''}
                </p>
              )}
              {currentSession && (
                <p className="text-xs text-muted-foreground">
                  Session ID: {currentSession.id}
                </p>
              )}
              {savingResults && (
                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  Saving results...
                </div>
              )}
            </div>

            <div className="flex flex-col gap-3">
              <Button
                onClick={startNewGame}
                size="lg"
                className="w-full py-3 text-lg"
              >
                🎮 Play Again
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="w-full py-3 text-lg"
                onClick={() => (window.location.href = "/")}
              >
                🏠 Return Home
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <div className="absolute top-25 left-10 z-10">
        <Badge
          variant="outline"
          className={cn(
            "w-14 h-14 rounded-full text-xl font-bold border-4 flex items-center justify-center shadow-lg",
            timeLeft <= 5
              ? "bg-destructive border-destructive text-white animate-pulse"
              : timeLeft <= 10
              ? "bg-yellow-500 border-yellow-600 text-white"
              : "bg-green-500 border-green-600 text-white"
          )}
        >
          {timeLeft}
        </Badge>
      </div>

      <div className="absolute top-25 right-10 z-10">
        <Badge
          variant="outline"
          className="px-3 py-2 text-sm font-bold bg-background/90 backdrop-blur-sm border-2"
        >
          {Math.min(currentQuestionIndex + 1, 5)}/5
        </Badge>
      </div>

      {playerName && questionsAnswered === 0 && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
          <Badge
            variant="outline"
            className="px-4 py-2 text-sm font-semibold bg-blue-600 text-white border-blue-700 shadow-lg"
          >
            Good luck, {playerName}! ⚡
          </Badge>
        </div>
      )}

      <div className="flex flex-col items-center p-2 space-y-3">
        <div className="relative">
          <div className="w-48 h-48 bg-card/20 rounded-full flex items-center justify-center backdrop-blur-sm border">
            <img
              src={getPokemonSpriteUrl(currentQuestion.pokemon_id)}
              alt={currentQuestion.pokemon_name}
              className="w-40 h-40 object-contain"
              onError={(e) => {
                (
                  e.target as HTMLImageElement
                ).src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${currentQuestion.pokemon_id}.png`;
              }}
            />
          </div>
          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
            <Badge
              variant="outline"
              className="bg-background/90 backdrop-blur-sm px-2 py-1 text-xs"
            >
              <span className="font-bold capitalize">
                {currentQuestion.pokemon_name}
              </span>
            </Badge>
          </div>
        </div>

        <Card className="max-w-2xl mx-auto w-full">
          <CardContent className="pt-3 pb-3 px-4">
            <h2 className="text-base sm:text-lg font-semibold text-center leading-relaxed">
              {currentQuestion.question}
            </h2>
          </CardContent>
        </Card>
      </div>

      <div className="flex-1 p-3 pb-4">
        {!showIntermediateCard ? (
          <div className="flex flex-col gap-2 max-w-4xl mx-auto">
            {Object.entries(currentQuestion.options).map(([key, value]) => (
              <Button
                key={key}
                onClick={() => handleAnswerSelect(key)}
                disabled={showResult}
                variant={getOptionVariant(key)}
                className={cn(
                  "flex items-start min-h-[60px] h-auto p-4 text-left justify-start hover:scale-[0.99] transition-all duration-200 overflow-hidden",
                  "text-xs sm:text-sm md:text-base leading-relaxed w-full",
                  getOptionClasses(key)
                )}
              >
                <span className="mr-3 sm:mr-4 font-bold text-sm sm:text-base md:text-lg flex-shrink-0 leading-tight">
                  {key}:
                </span>
                <span className="flex-1 min-w-0 text-left break-words whitespace-normal leading-relaxed overflow-wrap-anywhere hyphens-auto">
                  {value}
                </span>
              </Button>
            ))}
          </div>
        ) : (
          <Card className="max-w-4xl mx-auto">
            <CardContent className="p-6 space-y-6">
              <div className="text-center">
                <Badge
                  variant={
                    selectedAnswer === currentQuestion.correct_answer
                      ? "default"
                      : "destructive"
                  }
                  className="text-lg px-4 py-2"
                >
                  {selectedAnswer === currentQuestion.correct_answer
                    ? "🎉 Correct!"
                    : selectedAnswer
                    ? "❌ Wrong!"
                    : "⏰ Time's up!"}
                </Badge>
              </div>

              {currentQuestion.explanation && (
                <div className="text-center">
                  <p className="text-muted-foreground text-sm sm:text-base leading-relaxed break-words">
                    {currentQuestion.explanation}
                  </p>
                </div>
              )}

              <div className="flex justify-center gap-4">
                <Button
                  onClick={handleLike}
                  variant={currentQuestionRated && questionRatings.some(r => r.question_id === currentQuestion?.id && r.action === 'like') ? "default" : "outline"}
                  size="lg"
                  className="flex items-center gap-2 px-6"
                  disabled={currentQuestionRated || !currentQuestion?.id}
                >
                  👍 {currentQuestionRated && questionRatings.some(r => r.question_id === currentQuestion?.id && r.action === 'like') ? "Liked!" : "Like"}
                </Button>
                <Button
                  onClick={handleDislike}
                  variant={currentQuestionRated && questionRatings.some(r => r.question_id === currentQuestion?.id && r.action === 'dislike') ? "destructive" : "outline"}
                  size="lg"
                  className="flex items-center gap-2 px-6"
                  disabled={currentQuestionRated || !currentQuestion?.id}
                >
                  👎 {currentQuestionRated && questionRatings.some(r => r.question_id === currentQuestion?.id && r.action === 'dislike') ? "Disliked!" : "Dislike"}
                </Button>
              </div>

              {!currentQuestion?.id && (
                <div className="text-center">
                  <p className="text-xs text-muted-foreground">
                    Question rating not available
                  </p>
                </div>
              )}

              <div className="text-center">
                <Button
                  onClick={goToNextQuestion}
                  size="lg"
                  className="px-8 py-3 text-base shadow-lg"
                >
                  {questionsAnswered >= 5 ? "View Results" : "Next Question →"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
