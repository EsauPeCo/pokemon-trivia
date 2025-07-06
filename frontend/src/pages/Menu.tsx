import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router";

export function Menu() {
  return (
    <div className="flex flex-col items-center justify-start h-full px-5 gap-4">
      <Link className="w-full" to="/trivia">
        <Card className="w-full">
          <CardHeader className="flex flex-col justify-center">
            <CardTitle className="text-2xl sm:text-4xl lg:text-7xl font-light">
              NEW GAME
            </CardTitle>
          </CardHeader>
        </Card>
      </Link>
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
