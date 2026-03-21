"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { listBooks, type Book } from "@/lib/catalog";

type Paginated<T> = {
  results?: T[];
} & Record<string, unknown>;

export default function CatalogPage() {
  const [search, setSearch] = useState("");
  const [data, setData] = useState<Paginated<Book> | Book[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const books: Book[] = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    return (data.results ?? []) as Book[];
  }, [data]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await listBooks({ search: search.trim() || undefined });
      setData(res);
    } catch (e) {
      const err = e as ApiError;
      setError(err.detail || "Не удалось загрузить каталог");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Каталог книг</h1>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void load();
          }}
          className="flex gap-2"
        >
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Название / ISBN / автор…"
            className="w-72 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
          />
          <button
            disabled={loading}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            {loading ? "..." : "Найти"}
          </button>
        </form>
      </div>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {books.map((b) => (
          <Link
            key={b.id}
            href={`/book/${b.id}`}
            className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:border-zinc-700"
          >
            <div className="text-sm text-zinc-500 dark:text-zinc-400">
              {b.year} {b.isbn ? `• ISBN ${b.isbn}` : null}
            </div>
            <div className="mt-1 font-semibold leading-snug">{b.title}</div>
            {b.subtitle ? (
              <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                {b.subtitle}
              </div>
            ) : null}
          </Link>
        ))}
      </div>

      {!loading && books.length === 0 ? (
        <div className="text-sm text-zinc-600 dark:text-zinc-400">Ничего не найдено.</div>
      ) : null}
    </div>
  );
}

