import axios from "axios";
import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud } from "lucide-react";
import * as reportsApi from "../api/reports";

export default function UploadReport() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      setIsUploading(true);

      try {
        const report = await reportsApi.uploadReport(file);
        navigate(`/reports/${report.id}`);
      } catch (err: unknown) {
        if (axios.isAxiosError(err)) {
          setError(
            err.response?.data?.detail ??
              "Upload failed. Please try a different file."
          );
        } else {
          setError("Upload failed. Please try a different file.");
        }
      } finally {
        setIsUploading(false);
      }
    },
    [navigate]
  );

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-1 font-display text-2xl font-semibold">
        Upload a lab report
      </h1>

      <p className="mb-6 text-sm text-ink/60">
        PDF, PNG, JPEG, or TIFF — scanned or digital. We'll extract and
        interpret the values for you.
      </p>

      <label
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);

          const file = e.dataTransfer.files?.[0];

          if (file) {
            handleFile(file);
          }
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-16 text-center transition-colors ${
          isDragging
            ? "border-teal bg-teal-light/40"
            : "border-border bg-card"
        }`}
      >
        <UploadCloud
          className="mb-4 h-10 w-10 text-teal"
          aria-hidden="true"
        />

        <p className="font-medium text-ink">
          Drag & drop your report here
        </p>

        <p className="text-sm text-ink/50">
          or click to browse
        </p>

        <input
          type="file"
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.tiff"
          disabled={isUploading}
          onChange={(e) => {
            const file = e.target.files?.[0];

            if (file) {
              handleFile(file);
            }
          }}
        />
      </label>

      {isUploading && (
        <p className="mt-4 text-center text-sm text-ink/60">
          Uploading and starting analysis…
        </p>
      )}

      {error && (
        <p
          role="alert"
          className="mt-4 text-center text-sm text-coral"
        >
          {error}
        </p>
      )}

      <p className="mt-8 text-center text-xs text-ink/40">
        This application is intended only for educational and informational
        purposes and is NOT a substitute for professional medical advice,
        diagnosis, or treatment.
      </p>
    </div>
  );
}