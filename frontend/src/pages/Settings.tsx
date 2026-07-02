import { useState } from "react";
import { useForm } from "react-hook-form";
import { apiClient } from "../api/client";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../contexts/ThemeContext";

interface PasswordForm {
  current_password: string;
  new_password: string;
}

export default function Settings() {
  const { user } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PasswordForm>();

  async function onSubmit(values: PasswordForm) {
    setError(null);
    setMessage(null);
    try {
      await apiClient.post("/users/me/change-password", values);
      setMessage("Password updated successfully.");
      reset();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Could not update your password.");
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-6 font-display text-2xl font-semibold">Settings</h1>

      <section className="card mb-6">
        <h2 className="mb-4 font-display text-lg font-semibold">Profile</h2>
        <p className="text-sm text-ink/60">Name</p>
        <p className="mb-3 font-medium">{user?.full_name}</p>
        <p className="text-sm text-ink/60">Email</p>
        <p className="font-medium">{user?.email}</p>
      </section>

      <section className="card mb-6">
        <h2 className="mb-4 font-display text-lg font-semibold">Appearance</h2>
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink/70">Dark mode</span>
          <button
            role="switch"
            aria-checked={isDark}
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors ${isDark ? "bg-teal" : "bg-border"}`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
                isDark ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </section>

      <section className="card mb-6">
        <h2 className="mb-4 font-display text-lg font-semibold">Change password</h2>
        {message && <p className="mb-3 rounded-md bg-sage-light px-3 py-2 text-sm text-sage">{message}</p>}
        {error && <p className="mb-3 rounded-md bg-coral-light px-3 py-2 text-sm text-coral">{error}</p>}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label" htmlFor="current_password">Current password</label>
            <input
              id="current_password"
              type="password"
              className="input-field"
              {...register("current_password", { required: "Required" })}
            />
            {errors.current_password && <p className="mt-1 text-xs text-coral">{errors.current_password.message}</p>}
          </div>
          <div>
            <label className="label" htmlFor="new_password">New password</label>
            <input
              id="new_password"
              type="password"
              className="input-field"
              {...register("new_password", {
                required: "Required",
                minLength: { value: 8, message: "At least 8 characters" },
              })}
            />
            {errors.new_password && <p className="mt-1 text-xs text-coral">{errors.new_password.message}</p>}
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary">
            {isSubmitting ? "Updating…" : "Update password"}
          </button>
        </form>
      </section>

      <p className="text-center text-xs text-ink/40">
        This application is intended only for educational and informational purposes and is NOT a
        substitute for professional medical advice, diagnosis, or treatment.
      </p>
    </div>
  );
}
