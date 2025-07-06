import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./pages/Home.tsx";
import { createBrowserRouter, RouterProvider } from "react-router";
import { Pokedex } from "@/pages/Pokedex.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/pokedex",
    element: <Pokedex />,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <div className="min-h-screen p-6">
      <RouterProvider router={router} />
    </div>
  </StrictMode>
);
