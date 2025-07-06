import { Link } from "react-router";
import { Switch } from "@/components/ui/switch";
import { useTheme } from "@/components/theme-provider";
import { Moon, Sun } from "lucide-react";

export function Navbar() {
  const { theme, setTheme } = useTheme();

  const resolvedTheme =
    theme === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : theme;

  const handleThemeToggle = () => {
    setTheme(resolvedTheme === "dark" ? "light" : "dark");
  };

  return (
    <nav className="flex items-center justify-between bg-background border-b border-border p-4">
      <div className="flex items-center">
        <Link
          to="/"
          className="flex items-center hover:opacity-80 transition-opacity"
        >
          <img
            src="/International_Pokémon_logo.svg.png"
            alt="Pokemon Logo"
            className="h-10 w-auto"
          />
        </Link>
      </div>
      <div className="flex items-center space-x-3">
        <Sun className="w-4 h-4 text-foreground" />
        <Switch
          checked={resolvedTheme === "dark"}
          onCheckedChange={handleThemeToggle}
        />
        <Moon className="w-4 h-4 text-foreground" />
      </div>
    </nav>
  );
}
