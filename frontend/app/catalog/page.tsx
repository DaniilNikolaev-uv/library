"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { ApiError } from "@/lib/api";
import { listBooks, listCategories, type Book, type Category } from "@/lib/catalog";
import { Alert } from "../_components/ui/Alert";
import { Badge } from "../_components/ui/Badge";
import { Button } from "../_components/ui/Button";
import { Card, CardContent, CardHeader } from "../_components/ui/Card";
import { Checkbox } from "../_components/ui/Checkbox";
import { Input } from "../_components/ui/Input";
import { Select } from "../_components/ui/Select";

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
    <div className="space-y-5">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight text-[--color-text]">
          Каталог книг
        </h1>
        <div className="text-sm text-[--color-muted]">
          Позиции: <Badge variant="muted">{books.length}</Badge>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="text-sm font-medium text-[--color-text]">Фильтры</div>
        </CardHeader>
        <CardContent className="pt-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void load();
            }}
            className="grid grid-cols-1 gap-3 md:grid-cols-[1fr_120px_220px_auto_auto]"
          >
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Название / ISBN / автор…"
            />
            <Input
              value={year}
              onChange={(e) => setYear(e.target.value)}
              placeholder="Год"
              inputMode="numeric"
            />
            <Select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">Все категории</option>
              {categories.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </Select>
            <label className="flex h-9 items-center gap-2 rounded-md border border-[--color-border] bg-[--color-surface] px-3 text-sm text-[--color-muted]">
              <Checkbox
                checked={availableOnly}
                onChange={(e) => setAvailableOnly(e.target.checked)}
              />
              Только доступные
            </label>
            <Button disabled={loading}>{loading ? "..." : "Найти"}</Button>
          </form>
        </CardContent>
      </Card>

      {error ? (
        <Alert variant="danger">{error}</Alert>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {books.map((b) => (
          <Link
            key={b.id}
            href={`/book/${b.id}`}
            className="rounded-xl border border-[--color-border] bg-[--color-surface] p-4 transition-colors hover:bg-[--color-surface-2]"
          >
            <div className="flex gap-3">
              <img
                src={b.cover_url || b.cover_image || "https://placehold.co/120x180?text=No+Cover"}
                alt={`Обложка: ${b.title}`}
                className="h-[120px] w-[80px] rounded-md object-cover ring-1 ring-[--color-border]"
                loading="lazy"
              />
              <div className="min-w-0">
                <div className="text-sm text-[--color-muted]">
                  {b.year} {b.isbn ? `• ISBN ${b.isbn}` : null}
                </div>
                <div className="mt-1 font-semibold leading-snug text-[--color-text]">
                  {b.title}
                </div>
                {b.subtitle ? (
                  <div className="mt-1 text-sm text-[--color-muted]">
                    {b.subtitle}
                  </div>
                ) : null}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && books.length === 0 ? (
        <div className="text-sm text-[--color-muted]">Ничего не найдено.</div>
      ) : null}
    </div>
  );
}

