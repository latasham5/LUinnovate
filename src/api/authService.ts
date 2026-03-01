import apiClient from "./client.ts";

export interface BackendLoginResponse {
  session_token: string;
  user_id: string;
  name: string;
  role: string;
  department: string;
  deployment_mode: string;
}

export interface BackendUserProfile {
  employee_id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  department_id: string;
  clearance_level: string;
  manager_id: string | null;
}

export async function login(ssoToken: string): Promise<BackendLoginResponse> {
  const { data } = await apiClient.post<BackendLoginResponse>("/auth/login", {
    sso_token: ssoToken,
  });
  localStorage.setItem("pg_token", data.session_token);
  localStorage.setItem("pg_user", JSON.stringify(data));
  return data;
}

export function logout(): void {
  localStorage.removeItem("pg_token");
  localStorage.removeItem("pg_user");
}

export async function getProfile(employeeId: string): Promise<BackendUserProfile> {
  const { data } = await apiClient.get<BackendUserProfile>(`/auth/profile/${employeeId}`);
  return data;
}

export function getStoredUser(): BackendLoginResponse | null {
  const raw = localStorage.getItem("pg_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as BackendLoginResponse;
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
