"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getBook, type Book } from "@/lib/catalog";

export default function BookPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;

  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    void (async () => {
      try {
        const b = await getBook(id);
        setBook(b);
      } catch (e) {
        const err = e as ApiError;
        setError(err.detail || "Не удалось загрузить книгу");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) return <div className="text-sm text-zinc-600 dark:text-zinc-400">Загрузка…</div>;
  if (error)
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
        {error}
      </div>
    );
  if (!book) return null;

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <div className="flex flex-col gap-4 sm:flex-row">
          <img
            src={book.cover_url || book.cover_image || "https://placehold.co/200x300?text=No+Cover"}
            alt={`Обложка: ${book.title}`}
            className="h-[240px] w-[160px] rounded-lg object-cover ring-1 ring-zinc-200 dark:ring-zinc-800"
          />
          <div className="min-w-0">
            <div className="text-sm text-zinc-500 dark:text-zinc-400">
              {book.year} {book.isbn ? `• ISBN ${book.isbn}` : null}
            </div>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight">{book.title}</h1>
            {book.subtitle ? (
              <div className="mt-2 text-zinc-700 dark:text-zinc-300">{book.subtitle}</div>
            ) : null}
            {book.description ? (
              <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-zinc-600 dark:text-zinc-400">
                {book.description}
              </p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

