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
      className={[
        "rounded-md px-2 py-1 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-900",
        active ? "bg-zinc-100 dark:bg-zinc-900" : "",
      ].join(" ")}
    >
      {children}
    </Link>
  );
}

export function Header() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="border-b border-zinc-200 bg-white/70 backdrop-blur dark:border-zinc-800 dark:bg-black/50">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="font-semibold tracking-tight">
          Archeion
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

          <div className="ml-2 h-6 w-px bg-zinc-200 dark:bg-zinc-800" />

          {loading ? (
            <span className="px-2 text-sm text-zinc-500 dark:text-zinc-400">
              ...
            </span>
          ) : user ? (
            <div className="flex items-center gap-2">
              <span className="hidden text-sm text-zinc-600 dark:text-zinc-400 sm:block">
                {user.email}
              </span>
              <button
                onClick={() => {
                  logout();
                  window.location.href = "/";
                }}
                className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
              >
                Выйти
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
            >
              Вход
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

