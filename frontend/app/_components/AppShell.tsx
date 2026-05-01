"use client";

import Link from "next/link";
import { LibraryBig, LogOut, Menu, UserRound } from "lucide-react";
import { useMemo } from "react";

import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { getVisibleNavItems } from "./nav-items";
import { NavLink } from "./NavLink";

function UserActions() {
  const { user, loading, logout } = useAuth();

  if (loading) return <span className="text-sm text-muted-foreground">...</span>;
  if (!user) {
    return (
      <Button asChild size="sm">
        <Link href="/login">Вход</Link>
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="hidden max-w-[14rem] items-center gap-2 truncate rounded-md border border-border/70 bg-surface/70 px-2.5 py-1.5 text-xs text-muted-foreground sm:inline-flex">
        <UserRound className="h-3.5 w-3.5 text-[--accent-2]" />
        {user.email}
      </span>
      <Button
        size="sm"
        variant="secondary"
        onClick={() => {
          logout();
          window.location.href = "/";
        }}
      >
        <LogOut className="mr-1.5 h-3.5 w-3.5" />
        Выйти
      </Button>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const navItems = useMemo(() => getVisibleNavItems(user), [user]);

  return (
    <div className="min-h-dvh text-foreground">
      <header className="sticky top-0 z-20 border-b border-border/80 bg-background/72 backdrop-blur-xl">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-4 px-4">
          <Link href="/" className="group flex min-w-0 items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg border border-[--border-soft] bg-surface-2 text-[--accent-2] shadow-lg shadow-black/20 transition-transform group-hover:-rotate-3">
              <LibraryBig className="h-5 w-5" />
            </span>
            <span className="min-w-0">
              <span className="block font-[family-name:var(--font-display)] text-xl font-semibold leading-none tracking-normal">
                Archerion
              </span>
              <span className="mt-1 hidden text-[0.68rem] uppercase tracking-[0.22em] text-muted-foreground sm:block">
                Library OS
              </span>
            </span>
          </Link>

          <nav className="ml-4 hidden items-center gap-1 rounded-lg border border-border/70 bg-surface/55 p-1 shadow-inner shadow-black/10 md:flex">
            {navItems.map((item) => (
              <NavLink key={item.href} href={item.href}>
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <div className="hidden text-xs uppercase tracking-[0.24em] text-muted-foreground lg:block">
              Archive Control Surface
            </div>
            <UserActions />
            <div className="md:hidden">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="secondary" size="icon" aria-label="Открыть меню">
                    <Menu className="h-4 w-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-72 p-0">
                  <SheetHeader className="px-4 py-4">
                    <SheetTitle>Навигация</SheetTitle>
                  </SheetHeader>
                  <Separator />
                  <nav className="flex flex-col gap-1.5 p-3">
                    {navItems.map((item) => (
                      <NavLink key={item.href} href={item.href} vertical>
                        {item.label}
                      </NavLink>
                    ))}
                  </nav>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl px-4 py-6 lg:py-8">
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_16rem]">
          <div className="min-w-0">{children}</div>
          <aside className="hidden lg:block">
            <div className="app-panel sticky top-24 rounded-lg p-4">
              <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Быстрый доступ
              </div>
              <div className="mt-4 flex flex-col gap-1.5">
                {navItems.map((item) => (
                  <NavLink key={item.href} href={item.href} vertical>
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
