import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, FileText, TrendingUp, Upload } from "lucide-react";
import * as reportsApi from "../api/reports";
import type { DashboardStats } from "../types";
import LoadingSpinner from "../components/LoadingSpinner";
import ParameterChart from "../components/ParameterChart";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    reportsApi
      .getDashboardStats()
      .then(setStats)
      .catch(() => setError("Could not load your dashboard right now."));
  }, []);

  if (error) return <p className="p-8 text-center text-coral">{error}</p>;
  if (!stats) return <LoadingSpinner label="Loading your dashboard…" />;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Your health overview</h1>
          <p className="text-sm text-ink/60">A summary across all analyzed reports.</p>
        </div>
        <Link to="/upload" className="btn-primary">
          <Upload className="mr-2 h-4 w-4" /> Upload report
        </Link>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="card">
          <FileText className="mb-2 h-5 w-5 text-teal" />
          <p className="text-2xl font-semibold font-mono">{stats.total_reports}</p>
          <p className="text-sm text-ink/60">Total reports</p>
        </div>
        <div className="card">
          <TrendingUp className="mb-2 h-5 w-5 text-teal" />
          <p className="text-2xl font-semibold font-mono">
            {stats.average_health_score !== null ? stats.average_health_score.toFixed(1) : "—"}
          </p>
          <p className="text-sm text-ink/60">Average health score</p>
        </div>
        <div className="card">
          <AlertTriangle className="mb-2 h-5 w-5 text-coral" />
          <p className="text-2xl font-semibold font-mono">{stats.abnormal_parameter_count}</p>
          <p className="text-sm text-ink/60">Parameters outside range</p>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 font-display text-lg font-semibold">Health score trend</h2>
        <ParameterChart trend={stats.trend} />
      </div>

      <p className="mt-8 text-center text-xs text-ink/40">
        This application is intended only for educational and informational purposes and is NOT a
        substitute for professional medical advice, diagnosis, or treatment.
      </p>
    </div>
  );
}
