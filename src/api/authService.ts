import apiClient from "./client.ts";
import type { LoginResponse, UserProfile } from "../types/index.ts";

export async function login(ssoToken: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/auth/login", {
    sso_token: ssoToken,
  });
  localStorage.setItem("pg_token", data.access_token);
  localStorage.setItem("pg_user", JSON.stringify(data.user));
  return data;
}

export function logout(): void {
  localStorage.removeItem("pg_token");
  localStorage.removeItem("pg_user");
}

export async function getProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>("/auth/me");
  return data;
}

export function getStoredUser(): UserProfile | null {
  const raw = localStorage.getItem("pg_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
}

export function getStoredToken(): string | null {
  return localStorage.getItem("pg_token");
}

export function isAuthenticated(): boolean {
  return !!getStoredToken();
}
