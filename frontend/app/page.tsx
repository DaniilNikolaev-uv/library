"use client";

import Link from "next/link";
import { BookOpen, LayoutDashboard, LogIn, Search, UserPlus } from "lucide-react";

import { getHomeRouteForRole } from "@/lib/auth";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading } = useAuth();
  const accountHref = getHomeRouteForRole(user?.role);
  const accountLabel =
    user?.role === "admin"
      ? "В админ-панель"
      : user?.role === "librarian"
        ? "В панель сотрудника"
        : "В кабинет читателя";

  return (
    <div className="space-y-6">
      <section className="app-panel overflow-hidden rounded-lg p-6 md:p-8">
        <div className="grid gap-8 md:grid-cols-[1.25fr_0.75fr] md:items-end">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-md border border-border/80 bg-surface-2/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              <BookOpen className="h-3.5 w-3.5 text-[--accent-2]" />
              Library Control
            </div>
            <h1 className="max-w-2xl text-4xl font-semibold leading-[1.02] text-foreground md:text-6xl">
              Каталог без лишнего шума
            </h1>
            <p className="mt-4 max-w-xl text-sm leading-6 text-muted-foreground md:text-base">
              Поиск книг, выдачи, бронирования и штрафы собраны в спокойной рабочей панели.
            </p>
          </div>
          <div className="rounded-lg border border-border/80 bg-background/45 p-4">
            <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Состояние</div>
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-md bg-surface-2/70 p-3">
                <div className="text-2xl font-semibold text-foreground">4</div>
                <div className="mt-1 text-muted-foreground">роли</div>
              </div>
              <div className="rounded-md bg-surface-2/70 p-3">
                <div className="text-2xl font-semibold text-foreground">1</div>
                <div className="mt-1 text-muted-foreground">каталог</div>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/catalog"
            className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-lg shadow-blue-950/20 transition-all hover:-translate-y-0.5 hover:brightness-110"
          >
            <Search className="h-4 w-4" />
            Открыть каталог
          </Link>
          {!loading && user ? (
            <Link
              href={accountHref}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-surface/80 px-4 text-sm font-semibold text-foreground transition-all hover:-translate-y-0.5 hover:bg-surface-2"
            >
              <LayoutDashboard className="h-4 w-4" />
              {accountLabel}
            </Link>
          ) : null}
          {!loading && !user ? (
            <>
              <Link
                href="/login"
                className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-surface/80 px-4 text-sm font-semibold text-foreground transition-all hover:-translate-y-0.5 hover:bg-surface-2"
              >
                <LogIn className="h-4 w-4" />
                Войти
              </Link>
              <Link
                href="/register"
                className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-surface/80 px-4 text-sm font-semibold text-foreground transition-all hover:-translate-y-0.5 hover:bg-surface-2"
              >
                <UserPlus className="h-4 w-4" />
                Регистрация
              </Link>
            </>
          ) : null}
        </div>
      </section>
    </div>
  );
}
