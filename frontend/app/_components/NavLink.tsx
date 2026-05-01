"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/cn";

export function NavLink({
  href,
  children,
  vertical = false,
  onNavigate,
}: {
  href: string;
  children: React.ReactNode;
  vertical?: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const isActive = pathname === href || (href !== "/" && pathname?.startsWith(href));

  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "relative rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        vertical ? "block w-full px-3 py-2.5 text-left" : "inline-flex h-9 items-center px-3",
        isActive
          ? "bg-surface-2 text-foreground shadow-inner shadow-white/5 before:absolute before:left-1 before:top-1/2 before:h-5 before:w-0.5 before:-translate-y-1/2 before:rounded-full before:bg-[--accent-2]"
          : "text-muted-foreground hover:bg-surface-2/70 hover:text-foreground",
      )}
    >
      {children}
    </Link>
  );
}
