import { apiFetch, authStorage } from "./api";

export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "librarian" | "reader";
};

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

