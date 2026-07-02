import { Link } from "react-router-dom";
import { ShieldCheck, Sparkles, Upload } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-4xl px-6 py-16 text-center">
      <p className="mb-3 font-mono text-xs uppercase tracking-widest text-teal">Lab reports, understood</p>
      <h1 className="mb-4 font-display text-4xl font-semibold leading-tight sm:text-5xl">
        Turn a page of lab numbers into something you can actually read
      </h1>
      <p className="mx-auto mb-8 max-w-xl text-ink/60">
        Upload a pathology or blood-test report and get extracted values, plain-language context, and a
        tracked history — without ever being told what to diagnose.
      </p>

      <div className="mb-16 flex justify-center gap-3">
        <Link to={user ? "/upload" : "/register"} className="btn-primary">
          <Upload className="mr-2 h-4 w-4" /> Upload your first report
        </Link>
        {!user && (
          <Link to="/login" className="btn-secondary">Sign in</Link>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 text-left sm:grid-cols-3">
        <div className="card">
          <Upload className="mb-3 h-5 w-5 text-teal" />
          <h3 className="mb-1 font-medium">OCR & extraction</h3>
          <p className="text-sm text-ink/60">Scanned or digital PDFs, parsed into structured values automatically.</p>
        </div>
        <div className="card">
          <Sparkles className="mb-3 h-5 w-5 text-teal" />
          <h3 className="mb-1 font-medium">Plain-language summaries</h3>
          <p className="text-sm text-ink/60">Every result is explained clearly, with cautious, non-diagnostic wording.</p>
        </div>
        <div className="card">
          <ShieldCheck className="mb-3 h-5 w-5 text-teal" />
          <h3 className="mb-1 font-medium">Private by default</h3>
          <p className="text-sm text-ink/60">Your reports are tied to your account only, and never diagnosed.</p>
        </div>
      </div>

      <p className="mt-16 text-xs text-ink/40">
        This application is intended only for educational and informational purposes and is NOT a
        substitute for professional medical advice, diagnosis, or treatment.
      </p>
    </div>
  );
}
