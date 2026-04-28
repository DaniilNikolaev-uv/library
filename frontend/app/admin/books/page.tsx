"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import type { Book } from "@/lib/admin";
import { getBooks } from "@/lib/admin";
import { useAuth } from "@/lib/auth-context";

export default function AdminBooksPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) {
      router.replace("/login");
    }
  }, [authLoading, router, user]);

  useEffect(() => {
    if (user?.role === "admin") {
      void loadBooks();
    }
  }, [user]);

  async function loadBooks() {
    setLoading(true);
    try {
      const data = await getBooks();
      setBooks(data);
    } catch (error) {
      console.error("Failed to load books:", error);
    } finally {
      setLoading(false);
    }
  }

  const filteredBooks = books.filter(
    (b) =>
      b.title.toLowerCase().includes(search.toLowerCase()) ||
      b.authors.some((a) =>
        `${a.first_name} ${a.last_name}`.toLowerCase().includes(search.toLowerCase())
      ) ||
      (b.isbn && b.isbn.includes(search))
  );

  if (authLoading || !user || user.role !== "admin") {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Книги</h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Каталог книг
          </p>
        </div>
        <Link
          href="/admin"
          className="text-sm text-zinc-600 hover:underline dark:text-zinc-400"
        >
          ← Назад
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Поиск по названию, автору или ISBN..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-zinc-400 dark:border-zinc-800 dark:bg-black"
        />
      </div>

      {loading ? (
        <div className="py-12 text-center text-zinc-500">Загрузка...</div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
          <table className="w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Название
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Авторы
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  Год
                </th>
                <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-400">
                  ISBN
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredBooks.map((book) => (
                <tr
                  key={book.id}
                  className="border-b border-zinc-100 last:border-0 dark:border-zinc-900"
                >
                  <td className="px-4 py-3 font-medium">{book.title}</td>
                  <td className="px-4 py-3 text-zinc-600 dark:text-zinc-400">
                    {book.authors.map((a) => `${a.first_name} ${a.last_name}`).join(", ")}
                  </td>
                  <td className="px-4 py-3">{book.year}</td>
                  <td className="px-4 py-3 font-mono text-xs">{book.isbn || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredBooks.length === 0 && (
            <div className="py-12 text-center text-zinc-500">
              Книги не найдены
            </div>
          )}
        </div>
      )}
    </div>
  );
}
