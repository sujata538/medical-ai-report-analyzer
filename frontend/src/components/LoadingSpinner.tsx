export default function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-ink/60" role="status">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal border-t-transparent" />
      <span className="text-sm">{label}</span>
    </div>
  );
}
