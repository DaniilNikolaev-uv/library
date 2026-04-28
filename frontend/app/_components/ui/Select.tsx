"use client";

import type { SelectHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export function Select({
  className,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={cn(
        "h-9 w-full rounded-md border border-[--color-border] bg-[--color-surface] px-3 text-sm text-[--color-text]",
        "outline-none transition-colors focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-[--color-ring]",
        "disabled:pointer-events-none disabled:opacity-60",
        className,
      )}
    >
      {children}
    </select>
  );
}

