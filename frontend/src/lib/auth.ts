import { apiFetch, authStorage } from "./api";

export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "librarian" | "reader";
};

export function getHomeRouteForRole(role: User["role"] | undefined | null) {
  if (role === "admin") return "/admin";
  if (role === "librarian") return "/staff";
  return "/reader";
}

export async function login(email: string, password: string) {
  const res = await apiFetch<{ access: string; refresh: string }>(
    "/api/auth/login/",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
  );
  authStorage.setAccessToken(res.access);
  authStorage.setRefreshToken(res.refresh);
  return res;
}

export async function me() {
  return await apiFetch<User>("/api/auth/me/", { method: "GET" });
}

export function logout() {
  authStorage.clear();
}

export type RegisterReaderPayload = {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  address?: string;
};

export async function registerReader(payload: RegisterReaderPayload) {
  return await apiFetch("/api/auth/register-reader/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


