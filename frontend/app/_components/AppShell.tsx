"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
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
      <span className="hidden max-w-[14rem] truncate text-sm text-muted-foreground sm:block">
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
        Выйти
      </Button>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const navItems = useMemo(() => getVisibleNavItems(user), [user]);

  return (
    <div className="flex min-h-dvh bg-background text-foreground">
      <aside className="hidden w-60 shrink-0 border-r border-border bg-surface md:flex md:flex-col">
        <div className="px-4 py-4">
          <Link href="/" className="font-semibold tracking-tight">
            Archerion
          </Link>
        </div>
        <Separator />
        <nav className="flex flex-1 flex-col gap-1 p-2">
          {navItems.map((item) => (
            <NavLink key={item.href} href={item.href} vertical>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
          <div className="flex h-12 items-center justify-between gap-3 px-4">
            <div className="flex items-center gap-2 md:hidden">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="secondary" size="icon" aria-label="Открыть меню">
                    <Menu className="h-4 w-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-64 p-0">
                  <SheetHeader className="px-4 py-3">
                    <SheetTitle>Навигация</SheetTitle>
                  </SheetHeader>
                  <Separator />
                  <nav className="flex flex-col gap-1 p-2">
                    {navItems.map((item) => (
                      <NavLink key={item.href} href={item.href} vertical>
                        {item.label}
                      </NavLink>
                    ))}
                  </nav>
                </SheetContent>
              </Sheet>
              <Link href="/" className="font-semibold tracking-tight">
                Archerion
              </Link>
            </div>
            <div className="ml-auto">
              <UserActions />
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-4">{children}</main>
      </div>
    </div>
  );
}
