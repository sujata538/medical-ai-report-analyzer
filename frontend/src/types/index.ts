export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type ParameterFlag =
  | "low"
  | "normal"
  | "high"
  | "critical_low"
  | "critical_high"
  | "unknown";

export interface Parameter {
  id: string;
  name: string;
  raw_text: string;
  value: number;
  unit: string | null;
  flag: ParameterFlag;
  confidence: number;
  reference_low?: number | null;
  reference_high?: number | null;
}

export interface Recommendation {
  id: string;
  parameter_name: string | null;
  message: string;
  severity: "info" | "advisory" | "important";
}

export type ReportStatus = "uploaded" | "processing" | "extracted" | "analyzed" | "failed";

export interface ReportSummary {
  id: string;
  title: string;
  status: ReportStatus;
  health_score: number | null;
  risk_category: string | null;
  created_at: string;
}

export interface ReportDetail extends ReportSummary {
  ai_summary: string | null;
  raw_extracted_text: string | null;
  parameters: Parameter[];
  recommendations: Recommendation[];
}

export interface DashboardStats {
  total_reports: number;
  average_health_score: number | null;
  abnormal_parameter_count: number;
  latest_report_id: string | null;
  trend: { report_id: string; date: string; health_score: number }[];
}
