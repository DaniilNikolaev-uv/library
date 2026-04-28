"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getHomeRouteForRole, me } from "@/lib/auth";
import { myReservations, type Reservation } from "@/lib/reader";

type Paginated<T> = { results?: T[] } & Record<string, unknown>;

export default function ReaderReservationsPage() {
  const router = useRouter();
  const [data, setData] = useState<Paginated<Reservation> | Reservation[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reservations = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    return (data.results ?? []) as Reservation[];
  }, [data]);

  useEffect(() => {
    void (async () => {
      try {
        const user = await me();
        if (user.role !== "reader") {
          router.replace(getHomeRouteForRole(user.role));
          return;
        }
        const res = await myReservations();
        setData(res);
      } catch (e) {
        const err = e as ApiError;
        setError(err.detail || "Не удалось загрузить брони");
      }
    })();
  }, [router]);

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Мои брони</h1>
        </div>
        <Link href="/reader" className="text-sm underline">
          Назад
        </Link>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-3">
        {reservations.map((r) => (
          <div
            key={r.id}
            className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="font-medium">
                {r.book_title || "Книга"}{" "}
                <span className="text-zinc-500 dark:text-zinc-400">
                  {r.inventory_number ? `• #${r.inventory_number}` : null}
                </span>
              </div>
              <div className="text-sm text-zinc-600 dark:text-zinc-400">
                {r.status_display || r.status}
              </div>
            </div>
            <div className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
              Создано: {r.created_at} • Истекает: {r.expires_at}
            </div>
          </div>
        ))}
      </div>

      {reservations.length === 0 && !error ? (
        <div className="text-sm text-zinc-600 dark:text-zinc-400">Пока пусто.</div>
      ) : null}
    </div>
  );
}

