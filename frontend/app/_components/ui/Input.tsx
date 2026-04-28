"use client";

import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export function Input({
  className,
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "h-9 w-full rounded-md border border-[--color-border] bg-[--color-surface] px-3 text-sm text-[--color-text]",
        "placeholder:text-[--color-muted]",
        "outline-none transition-colors focus-visible:border-blue-500 focus-visible:ring-2 focus-visible:ring-[--color-ring]",
        "disabled:pointer-events-none disabled:opacity-60",
        className,
      )}
    />
  );
}

