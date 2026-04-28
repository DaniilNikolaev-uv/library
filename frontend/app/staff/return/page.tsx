"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getHomeRouteForRole, me } from "@/lib/auth";
import { returnLoan } from "@/lib/staff";

export default function StaffReturnPage() {
  const router = useRouter();
  const [loanId, setLoanId] = useState("");
  const [markLost, setMarkLost] = useState(false);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const user = await me();
        if (user.role !== "librarian" && user.role !== "admin") {
          router.replace(getHomeRouteForRole(user.role));
        }
      } catch {
        router.replace("/login");
      }
    })();
  }, [router]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await returnLoan({ loan_id: Number(loanId), mark_lost: markLost });
      setResult(res);
    } catch (e) {
      const err = e as ApiError;
      setError(err.detail || "Не удалось оформить возврат");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Возврат</h1>
        </div>
        <Link href="/staff" className="text-sm underline">
          Назад
        </Link>
      </div>

      <form
        onSubmit={onSubmit}
        className="max-w-xl rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
      >
        <div className="grid gap-3">
          <label className="block text-sm">
            <span className="text-zinc-700 dark:text-zinc-300">ID выдачи (loan_id)</span>
            <input
              value={loanId}
              onChange={(e) => setLoanId(e.target.value)}
              inputMode="numeric"
              className="mt-1 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
              required
            />
          </label>

          <label className="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
            <input
              type="checkbox"
              checked={markLost}
              onChange={(e) => setMarkLost(e.target.checked)}
            />
            Пометить как утерянную
          </label>

          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
              {error}
            </div>
          ) : null}

          <button
            disabled={loading}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            {loading ? "Оформляем..." : "Оформить возврат"}
          </button>
        </div>
      </form>

      {result ? (
        <pre className="overflow-auto rounded-2xl border border-zinc-200 bg-white p-4 text-xs dark:border-zinc-800 dark:bg-zinc-950">
          {JSON.stringify(result, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}

