import { Link } from "react-router-dom";
import { FileText } from "lucide-react";
import type { ReportSummary } from "../types";

const STATUS_LABEL: Record<string, string> = {
  uploaded: "Uploaded",
  processing: "Processing…",
  extracted: "Extracting…",
  analyzed: "Analyzed",
  failed: "Failed",
};

const RISK_COLOR: Record<string, string> = {
  excellent: "bg-sage-light text-sage",
  good: "bg-sage-light text-sage",
  moderate: "bg-yellow-100 text-yellow-800",
  elevated: "bg-coral-light text-coral",
  high: "bg-coral-light text-coral",
};

export default function ReportCard({ report }: { report: ReportSummary }) {
  return (
    <Link
      to={`/reports/${report.id}`}
      className="card flex items-center justify-between gap-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center gap-4">
        <div className="rounded-md bg-teal-light p-3">
          <FileText className="h-5 w-5 text-teal-dark" aria-hidden="true" />
        </div>
        <div>
          <p className="font-medium text-ink">{report.title}</p>
          <p className="text-sm text-ink/60">
            {new Date(report.created_at).toLocaleDateString()} · {STATUS_LABEL[report.status] ?? report.status}
          </p>
        </div>
      </div>

      <div className="text-right">
        {report.health_score !== null ? (
          <>
            <p className="font-mono text-lg font-semibold text-ink">{report.health_score}</p>
            {report.risk_category && (
              <span
                className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                  RISK_COLOR[report.risk_category] ?? "bg-surface text-ink/60"
                }`}
              >
                {report.risk_category}
              </span>
            )}
          </>
        ) : (
          <span className="text-sm text-ink/40">—</span>
        )}
      </div>
    </Link>
  );
}
