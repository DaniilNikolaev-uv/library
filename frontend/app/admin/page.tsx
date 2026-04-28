"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { useAuth } from "@/lib/auth-context";
import type { User as UserType, Book, Loan, Reader } from "@/lib/admin";
import { getUsers, getBooks, getLoans, getReaders } from "@/lib/admin";

type Stats = {
  users: number;
  books: number;
  activeLoans: number;
  readers: number;
};

export default function AdminPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (user?.role === "admin") {
      loadStats();
    }
  }, [user]);

  async function loadStats() {
    setIsLoading(true);
    try {
      const [users, books, loans, readers] = await Promise.all([
        getUsers(),
        getBooks(),
        getLoans(),
        getReaders(),
      ]);
      setStats({
        users: users.length,
        books: books.length,
        activeLoans: loans.filter((l) => l.status === "active").length,
        readers: readers.length,
      });
    } catch (error) {
      console.error("Failed to load stats:", error);
    } finally {
      setIsLoading(false);
    }
  }

  if (loading || !user || user.role !== "admin") {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Админ-панель</h1>
        <span className="text-sm text-zinc-600 dark:text-zinc-400">
          {user.email}
        </span>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <span className="text-zinc-500">Загрузка...</span>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Пользователи"
              value={stats?.users ?? 0}
              href="/admin/users"
            />
            <StatCard
              title="Книги"
              value={stats?.books ?? 0}
              href="/admin/books"
            />
            <StatCard
              title="Активные выдачи"
              value={stats?.activeLoans ?? 0}
              href="/admin/loans"
            />
            <StatCard
              title="Читатели"
              value={stats?.readers ?? 0}
              href="/admin/readers"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <AdminCard title="Пользователи" href="/admin/users">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Управление пользователями, ролями и доступом
              </p>
            </AdminCard>
            <AdminCard title="Читатели" href="/admin/readers">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Управление читателями и их профилями
              </p>
            </AdminCard>
            <AdminCard title="Книги" href="/admin/books">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Каталог книг, авторы, издатели
              </p>
            </AdminCard>
            <AdminCard title="Выдачи" href="/admin/loans">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Выдача и возврат книг
              </p>
            </AdminCard>
            <AdminCard title="Audit Timeline" href="/admin/audit">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Лента действий по книгам, выдачам, броням и штрафам
              </p>
            </AdminCard>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  href,
}: {
  title: string;
  value: number;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm transition-colors hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
    >
      <div className="text-sm text-zinc-600 dark:text-zinc-400">{title}</div>
      <div className="mt-1 text-3xl font-semibold tracking-tight">{value}</div>
    </Link>
  );
}

function AdminCard({
  title,
  children,
  href,
}: {
  title: string;
  children: React.ReactNode;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm transition-colors hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
    >
      <h3 className="font-medium">{title}</h3>
      <div className="mt-2">{children}</div>
    </Link>
  );
}
