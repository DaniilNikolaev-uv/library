"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getHomeRouteForRole, me, type User } from "@/lib/auth";
import { getDashboardStats, type StaffDashboardStats } from "@/lib/staff";

export default function StaffHome() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<StaffDashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const u = await me();
        if (u.role !== "librarian" && u.role !== "admin") {
          router.replace(getHomeRouteForRole(u.role));
          return;
        }
        setUser(u);
        const dashboardStats = await getDashboardStats();
        setStats(dashboardStats);
      } catch (e) {
        const err = e as ApiError;
        setError(err.detail || "Нужно войти");
      } finally {
        setStatsLoading(false);
      }
    })();
  }, [router]);

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold tracking-tight">Кабинет сотрудника</h1>
        {user ? (
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            {user.first_name} {user.last_name} • {user.email} • роль: {user.role}
          </p>
        ) : null}
        {error ? (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
            {error} — <Link className="underline" href="/login">войти</Link>
          </div>
        ) : null}
        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            href="/staff/issue"
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            Выдача
          </Link>
          <Link
            href="/staff/return"
            className="rounded-lg border border-zinc-200 px-4 py-2 text-sm font-medium hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900"
          >
            Возврат
          </Link>
        </div>
      </div>

      {statsLoading ? (
        <div className="rounded-2xl border border-zinc-200 bg-white p-6 text-sm text-zinc-500 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
          Загружаем статистику...
        </div>
      ) : stats ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Пользователи" value={stats.users} />
          <StatCard title="Книги" value={stats.books} />
          <StatCard title="Активные выдачи" value={stats.active_loans} />
          <StatCard title="Читатели" value={stats.readers} />
        </div>
      ) : null}
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="text-sm text-zinc-600 dark:text-zinc-400">{title}</div>
      <div className="mt-1 text-3xl font-semibold tracking-tight">{value}</div>
    </div>
  );
}
