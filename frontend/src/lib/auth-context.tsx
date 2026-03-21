"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import type { ApiError } from "./api";
import { authStorage } from "./api";
import { logout as doLogout, me, type User } from "./auth";

type AuthState = {
  user: User | null;
  loading: boolean;
  error: string | null;
  refresh(): Promise<void>;
  logout(): void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    const token = authStorage.getAccessToken();
    if (!token) {
      setUser(null);
      setError(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const u = await me();
      setUser(u);
      setError(null);
    } catch (e) {
      const err = e as ApiError;
      setUser(null);
      setError(err.detail || "Auth failed");
      authStorage.clear();
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    doLogout();
    setUser(null);
    setError(null);
  }

  useEffect(() => {
    void refresh();
  }, []);

  const value = useMemo<AuthState>(
    () => ({ user, loading, error, refresh, logout }),
    [user, loading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

