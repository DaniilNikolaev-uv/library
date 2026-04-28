"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { listBooks, listCategories, type Book, type Category } from "@/lib/catalog";

type Paginated<T> = {
  results?: T[];
} & Record<string, unknown>;

export default function CatalogPage() {
  const [search, setSearch] = useState("");
  const [year, setYear] = useState("");
  const [category, setCategory] = useState("");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [data, setData] = useState<Paginated<Book> | Book[] | null>(null);
  const [categoriesData, setCategoriesData] = useState<Paginated<Category> | Category[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const books: Book[] = useMemo(() => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    return (data.results ?? []) as Book[];
  }, [data]);

  const categories: Category[] = useMemo(() => {
    if (!categoriesData) return [];
    if (Array.isArray(categoriesData)) return categoriesData;
    return (categoriesData.results ?? []) as Category[];
  }, [categoriesData]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const res = await listBooks({
        search: search.trim() || undefined,
        year: year.trim() || undefined,
        category: category || undefined,
        available_only: availableOnly,
      });
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

  useEffect(() => {
    void (async () => {
      try {
        const res = await listCategories();
        setCategoriesData(res);
      } catch {
        setCategoriesData([]);
      }
    })();
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
          className="flex flex-wrap gap-2"
        >
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Название / ISBN / автор…"
            className="w-72 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
          />
          <input
            value={year}
            onChange={(e) => setYear(e.target.value)}
            placeholder="Год"
            inputMode="numeric"
            className="w-28 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-52 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
          >
            <option value="">Все категории</option>
            {categories.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-2 rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-800">
            <input
              checked={availableOnly}
              onChange={(e) => setAvailableOnly(e.target.checked)}
              type="checkbox"
            />
            Только доступные
          </label>
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
            <div className="flex gap-3">
              <img
                src={b.cover_url || b.cover_image || "https://placehold.co/120x180?text=No+Cover"}
                alt={`Обложка: ${b.title}`}
                className="h-[120px] w-[80px] rounded-md object-cover ring-1 ring-zinc-200 dark:ring-zinc-800"
                loading="lazy"
              />
              <div className="min-w-0">
                <div className="text-sm text-zinc-500 dark:text-zinc-400">
                  {b.year} {b.isbn ? `• ISBN ${b.isbn}` : null}
                </div>
                <div className="mt-1 font-semibold leading-snug">{b.title}</div>
                {b.subtitle ? (
                  <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                    {b.subtitle}
                  </div>
                ) : null}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && books.length === 0 ? (
        <div className="text-sm text-zinc-600 dark:text-zinc-400">Ничего не найдено.</div>
      ) : null}
    </div>
  );
}

