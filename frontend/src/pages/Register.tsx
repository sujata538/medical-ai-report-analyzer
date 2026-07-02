import axios from "axios";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
}

export default function Register() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();

  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>();

  async function onSubmit(values: RegisterForm) {
    setServerError(null);

    try {
      await registerUser(
        values.email,
        values.full_name,
        values.password
      );

      navigate("/dashboard");
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setServerError(
          err.response?.data?.detail ??
            "Could not create your account."
        );
      } else {
        setServerError("Could not create your account.");
      }
    }
  }

  return (
    <div className="mx-auto flex min-h-[80vh] max-w-md flex-col justify-center px-6">
      <h1 className="mb-1 font-display text-2xl font-semibold">
        Create your account
      </h1>

      <p className="mb-6 text-sm text-ink/60">
        Start tracking your lab reports securely.
      </p>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="card space-y-4"
      >
        {serverError && (
          <p
            role="alert"
            className="rounded-md bg-coral-light px-3 py-2 text-sm text-coral"
          >
            {serverError}
          </p>
        )}

        <div>
          <label className="label" htmlFor="full_name">
            Full name
          </label>

          <input
            id="full_name"
            className="input-field"
            {...register("full_name", {
              required: "Full name is required",
            })}
          />

          {errors.full_name && (
            <p className="mt-1 text-xs text-coral">
              {errors.full_name.message}
            </p>
          )}
        </div>

        <div>
          <label className="label" htmlFor="email">
            Email
          </label>

          <input
            id="email"
            type="email"
            className="input-field"
            {...register("email", {
              required: "Email is required",
            })}
          />

          {errors.email && (
            <p className="mt-1 text-xs text-coral">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <label className="label" htmlFor="password">
            Password
          </label>

          <input
            id="password"
            type="password"
            className="input-field"
            {...register("password", {
              required: "Password is required",
              minLength: {
                value: 8,
                message: "At least 8 characters",
              },
            })}
          />

          {errors.password && (
            <p className="mt-1 text-xs text-coral">
              {errors.password.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full"
        >
          {isSubmitting
            ? "Creating account…"
            : "Create account"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-ink/60">
        Already have an account?{" "}
        <Link
          to="/login"
          className="font-medium text-teal"
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}