import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./pages/Home.tsx";
import { createBrowserRouter, RouterProvider } from "react-router";
import { Pokedex } from "@/pages/Pokedex.tsx";
import { Layout } from "@/components/Layout";
import { ThemeProvider } from "@/components/theme-provider";

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
