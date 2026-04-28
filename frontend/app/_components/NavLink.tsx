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
        "rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        vertical ? "block w-full px-3 py-2 text-left" : "inline-flex px-2 py-1",
        isActive
          ? "bg-surface-2 text-foreground"
          : "text-muted-foreground hover:bg-surface-2 hover:text-foreground",
      )}
    >
      {children}
    </Link>
  );
}
