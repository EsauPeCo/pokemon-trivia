import { Navbar } from "@/components/Navbar";
import { Outlet } from "react-router";

export function Layout() {
  return (
    <div>
      <Navbar />
      <div className="p-6">
        <Outlet />
      </div>
    </div>
  );
} 