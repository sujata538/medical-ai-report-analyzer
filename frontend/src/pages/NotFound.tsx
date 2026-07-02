import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-lg flex-col items-center justify-center px-6 text-center">
      <p className="font-mono text-sm text-teal">404</p>
      <h1 className="mb-2 font-display text-2xl font-semibold">Page not found</h1>
      <p className="mb-6 text-sm text-ink/60">The page you're looking for doesn't exist or has moved.</p>
      <Link to="/" className="btn-primary">Back to home</Link>
    </div>
  );
}
