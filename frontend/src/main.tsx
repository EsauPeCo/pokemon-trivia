import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./pages/Home.tsx";
import { createBrowserRouter, RouterProvider } from "react-router";
import { Pokedex } from "@/pages/Pokedex.tsx";
import { PokemonDetail } from "@/pages/PokemonDetail.tsx";
import { Layout } from "@/components/Layout";
import { ThemeProvider } from "@/components/theme-provider";
import { Menu } from "@/pages/Menu.tsx";
import { Trivia } from "@/pages/Trivia.tsx";
import { GameIntro } from "@/pages/GameIntro.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/pokedex",
        element: <Pokedex />,
      },
      {
        path: "/pokemon/:id",
        element: <PokemonDetail />,
      },
      {
        path: "/menu",
        element: <Menu />,
      },
      {
        path: "/game-intro",
        element: <GameIntro />,
      },
      {
        path: "/trivia/:playerId",
        element: <Trivia />,
      },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <RouterProvider router={router} />
    </ThemeProvider>
  </StrictMode>
);
