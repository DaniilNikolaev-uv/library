"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import type { ApiError } from "@/lib/api";
import { getBook, type Book } from "@/lib/catalog";
import { Alert } from "../../_components/ui/Alert";
import { Badge } from "../../_components/ui/Badge";
import { Card, CardContent } from "../../_components/ui/Card";

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

  if (loading) return <div className="text-sm text-[--color-muted]">Загрузка…</div>;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!book) return null;

  return (
    <div className="space-y-5">
      <Card>
        <CardContent>
          <div className="flex flex-col gap-5 sm:flex-row">
            <img
              src={
                book.cover_url ||
                book.cover_image ||
                "https://placehold.co/200x300?text=No+Cover"
              }
              alt={`Обложка: ${book.title}`}
              className="h-[252px] w-[168px] rounded-md object-cover ring-1 ring-[--color-border]"
            />
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                {book.year ? <Badge variant="muted">{book.year}</Badge> : null}
                {book.isbn ? <Badge variant="muted">{`ISBN ${book.isbn}`}</Badge> : null}
              </div>

              <h1 className="mt-3 text-2xl font-semibold tracking-tight text-[--color-text]">
                {book.title}
              </h1>

              {book.subtitle ? (
                <div className="mt-2 text-sm text-[--color-muted]">{book.subtitle}</div>
              ) : null}

              <div className="mt-5 border-t border-[--color-border] pt-4">
                {book.description ? (
                  <p className="whitespace-pre-wrap text-sm leading-6 text-[--color-muted]">
                    {book.description}
                  </p>
                ) : (
                  <div className="text-sm text-[--color-muted]">
                    Описание отсутствует.
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

