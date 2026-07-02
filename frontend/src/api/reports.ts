import { apiClient } from "./client";
import type { DashboardStats, ReportDetail, ReportSummary } from "../types";

export async function uploadReport(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<ReportSummary>("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listReports(page = 1, pageSize = 20, search?: string) {
  const { data } = await apiClient.get<{ total: number; page: number; page_size: number; items: ReportSummary[] }>(
    "/reports",
    { params: { page, page_size: pageSize, search } }
  );
  return data;
}

export async function getReport(id: string) {
  const { data } = await apiClient.get<ReportDetail>(`/reports/${id}`);
  return data;
}

export async function deleteReport(id: string) {
  await apiClient.delete(`/reports/${id}`);
}

export async function getDashboardStats() {
  const { data } = await apiClient.get<DashboardStats>("/dashboard/stats");
  return data;
}

export function exportReportPdfUrl(id: string) {
  return `/api/v1/reports/${id}/export/pdf`;
}
