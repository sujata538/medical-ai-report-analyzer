import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import * as reportsApi from "../api/reports";
import type { ReportSummary } from "../types";
import ReportCard from "../components/ReportCard";
import LoadingSpinner from "../components/LoadingSpinner";

export default function History() {
  const [reports, setReports] = useState<ReportSummary[] | null>(null);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timeout = setTimeout(() => {
      reportsApi
        .listReports(1, 50, search || undefined)
        .then((data) => setReports(data.items))
        .catch(() => setError("Could not load your report history."));
    }, 300); // debounce search input
    return () => clearTimeout(timeout);
  }, [search]);

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="mb-1 font-display text-2xl font-semibold">Report history</h1>
      <p className="mb-6 text-sm text-ink/60">Every report you've uploaded, searchable by title.</p>

      <div className="relative mb-6">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink/40" />
        <input
          className="input-field pl-9"
          placeholder="Search reports…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <p className="text-coral">{error}</p>}
      {!reports && !error && <LoadingSpinner />}

      {reports && reports.length === 0 && (
        <p className="py-16 text-center text-sm text-ink/50">
          No reports found{search ? ` matching "${search}"` : " yet"}.
        </p>
      )}

      <div className="space-y-3">
        {reports?.map((report) => (
          <ReportCard key={report.id} report={report} />
        ))}
      </div>
    </div>
  );
}
