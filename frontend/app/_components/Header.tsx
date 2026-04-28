"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/lib/auth-context";

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const active = pathname === href || (href !== "/" && pathname?.startsWith(href));
  return (
    <Link
      href={href}
      className={`rounded-md px-2 py-1 text-sm transition-colors ${
        active
          ? "bg-[--color-surface-2] text-[--color-text]"
          : "text-[--color-muted] hover:bg-[--color-surface-2] hover:text-[--color-text]"
      }`}
    >
      {children}
    </Link>
  );
}

export function Header() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="sticky top-0 z-20 border-b border-[--color-border] bg-[--color-bg]/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-semibold tracking-tight text-[--color-text]">
          Archerion
        </Link>

        <nav className="flex items-center gap-2">
          <NavLink href="/catalog">Каталог</NavLink>
          <NavLink href="/reader">Читатель</NavLink>
          {user?.role === "admin" && (
            <NavLink href="/admin">Админ</NavLink>
          )}
          {user?.role === "librarian" && (
            <NavLink href="/staff">Сотрудник</NavLink>
          )}

          <div className="ml-2 h-6 w-px bg-[--color-border]" />

          {loading ? (
            <span className="px-2 text-sm text-[--color-muted]">
              ...
            </span>
          ) : user ? (
            <div className="flex items-center gap-2">
              <span className="hidden text-sm text-[--color-muted] sm:block">
                {user.email}
              </span>
              <button
                onClick={() => {
                  logout();
                  window.location.href = "/";
                }}
                className="rounded-md border border-[--color-border] bg-[--color-surface] px-3 py-1.5 text-sm font-medium text-[--color-text] transition-colors hover:bg-[--color-surface-2]"
              >
                Выйти
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="rounded-md bg-[--color-accent] px-3 py-1.5 text-sm font-medium text-[--color-accent-foreground] transition-colors hover:bg-blue-500"
            >
              Вход
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

