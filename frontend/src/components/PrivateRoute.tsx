import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import LoadingSpinner from "./LoadingSpinner";

export default function PrivateRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner label="Checking your session…" />;
  if (!user) return <Navigate to="/login" replace />;

  return <Outlet />;
}
