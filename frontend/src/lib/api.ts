export type ApiError = {
  status: number;
  detail: string;
  data?: unknown;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (!token) localStorage.removeItem("access_token");
  else localStorage.setItem("access_token", token);
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

function setRefreshToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (!token) localStorage.removeItem("refresh_token");
  else localStorage.setItem("refresh_token", token);
}

async function parseError(res: Response): Promise<ApiError> {
  let data: unknown = undefined;
  try {
    data = await res.json();
  } catch {
    // ignore
  }
  const maybeObj = typeof data === "object" && data !== null ? (data as Record<string, unknown>) : null;
  const detail =
    (typeof maybeObj?.detail === "string" ? (maybeObj.detail as string) : undefined) ||
    (typeof data === "string" ? data : undefined) ||
    res.statusText ||
    "Request failed";
  return { status: res.status, detail, data };
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const res = await fetch(`${API_BASE_URL}/api/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) return null;
  const json = (await res.json()) as { access: string };
  if (!json?.access) return null;
  setToken(json.access);
  return json.access;
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = path.startsWith("http")
    ? path
    : `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;

  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let res = await fetch(url, { ...init, headers });
  if (res.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      headers.set("Authorization", `Bearer ${newToken}`);
      res = await fetch(url, { ...init, headers });
    }
  }

  if (!res.ok) throw await parseError(res);

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const authStorage = {
  getAccessToken: getToken,
  setAccessToken: setToken,
  getRefreshToken,
  setRefreshToken,
  clear() {
    setToken(null);
    setRefreshToken(null);
  },
};

