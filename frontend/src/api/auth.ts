import { apiClient } from "./client";
import type { Tokens, User } from "../types";

export async function login(email: string, password: string) {
  const { data } = await apiClient.post<{ user: User; tokens: Tokens }>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function register(email: string, full_name: string, password: string) {
  const { data } = await apiClient.post<User>("/auth/register", { email, full_name, password });
  return data;
}

export async function getCurrentUser() {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}

export async function logout(refresh_token: string) {
  await apiClient.post("/auth/logout", { refresh_token });
}
