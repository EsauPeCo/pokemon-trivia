import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./pages/Home.tsx";
import { createBrowserRouter, RouterProvider } from "react-router";
import { Pokedex } from "@/pages/Pokedex.tsx";
import { Layout } from "@/components/Layout";
import { ThemeProvider } from "@/components/theme-provider";
import { Menu } from "@/pages/Menu.tsx";

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
        path: "/menu",
        element: <Menu />,
      },
      {
        path: "/trivia",
        element: (
          <div className="text-center py-20">
            <h1 className="text-4xl font-bold">Pokemon Trivia Coming Soon!</h1>
          </div>
        ),
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
