import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Download, RefreshCw } from "lucide-react";
import * as reportsApi from "../api/reports";
import type { ReportDetail as ReportDetailType } from "../types";
import LoadingSpinner from "../components/LoadingSpinner";

const FLAG_STYLE: Record<string, string> = {
  normal: "bg-sage-light text-sage",
  low: "bg-yellow-100 text-yellow-800",
  high: "bg-yellow-100 text-yellow-800",
  critical_low: "bg-coral-light text-coral",
  critical_high: "bg-coral-light text-coral",
  unknown: "bg-surface text-ink/50",
};

export default function ReportDetail() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<ReportDetailType | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!id) return;
    try {
      const data = await reportsApi.getReport(id);
      setReport(data);
    } catch {
      setError("Could not load this report.");
    }
  }

  useEffect(() => {
    load();
    // Poll while the report is still processing.
    const interval = setInterval(() => {
      setReport((current) => {
        if (current && (current.status === "analyzed" || current.status === "failed")) {
          clearInterval(interval);
        } else {
          load();
        }
        return current;
      });
    }, 3000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (error) return <p className="p-8 text-center text-coral">{error}</p>;
  if (!report) return <LoadingSpinner label="Loading report…" />;

  if (report.status !== "analyzed" && report.status !== "failed") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16 text-center">
        <RefreshCw className="mx-auto mb-4 h-8 w-8 animate-spin text-teal" />
        <p className="font-medium">Analyzing your report…</p>
        <p className="text-sm text-ink/60">This usually takes a few seconds. This page will update automatically.</p>
      </div>
    );
  }

  if (report.status === "failed") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16 text-center">
        <p className="font-medium text-coral">We couldn't analyze this report.</p>
        <p className="text-sm text-ink/60">Try uploading a clearer scan or a different file format.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">{report.title}</h1>
          <p className="text-sm text-ink/60">{new Date(report.created_at).toLocaleString()}</p>
        </div>
        <a href={reportsApi.exportReportPdfUrl(report.id)} className="btn-secondary" target="_blank" rel="noreferrer">
          <Download className="mr-2 h-4 w-4" /> Export PDF
        </a>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="card">
          <p className="text-sm text-ink/60">Health score</p>
          <p className="font-mono text-3xl font-semibold">{report.health_score}/100</p>
          <p className="text-sm capitalize text-ink/60">{report.risk_category} risk</p>
        </div>
        <div className="card">
          <p className="mb-1 text-sm text-ink/60">AI summary</p>
          <p className="whitespace-pre-line text-sm text-ink/80">{report.ai_summary}</p>
        </div>
      </div>

      <div className="card mb-6">
        <h2 className="mb-4 font-display text-lg font-semibold">Extracted parameters</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-ink/50">
                <th className="pb-2">Parameter</th>
                <th className="pb-2">Value</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {report.parameters.map((p) => (
                <tr key={p.id} className="border-b border-border last:border-0">
                  <td className="py-2 font-medium">{p.name}</td>
                  <td className="py-2 font-mono">{p.value}{p.unit ?? ""}</td>
                  <td className="py-2">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${FLAG_STYLE[p.flag]}`}>
                      {p.flag.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 font-display text-lg font-semibold">Recommendations</h2>
        <ul className="space-y-3">
          {report.recommendations.map((r) => (
            <li key={r.id} className="text-sm text-ink/80">
              {r.parameter_name && <span className="font-medium">{r.parameter_name}: </span>}
              {r.message}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
