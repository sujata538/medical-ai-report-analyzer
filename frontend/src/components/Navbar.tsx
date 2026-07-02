import { Link, useNavigate } from "react-router-dom";
import { Activity, LogOut, Moon, Sun } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../contexts/ThemeContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <header className="border-b border-border bg-card/80 backdrop-blur sticky top-0 z-10">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-display text-xl font-semibold text-ink">
          <Activity className="h-5 w-5 text-teal" aria-hidden="true" />
          MedInsight
        </Link>

        {user && (
          <div className="hidden gap-6 text-sm font-medium text-ink/70 md:flex">
            <Link to="/dashboard" className="hover:text-teal">Dashboard</Link>
            <Link to="/upload" className="hover:text-teal">Upload</Link>
            <Link to="/history" className="hover:text-teal">History</Link>
            <Link to="/settings" className="hover:text-teal">Settings</Link>
          </div>
        )}

        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
            className="rounded-md p-2 text-ink/60 hover:bg-surface hover:text-ink"
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          {user ? (
            <button onClick={handleLogout} className="btn-secondary" aria-label="Log out">
              <LogOut className="mr-2 h-4 w-4" /> Log out
            </button>
          ) : (
            <Link to="/login" className="btn-primary">Sign in</Link>
          )}
        </div>
      </nav>
    </header>
  );
}
