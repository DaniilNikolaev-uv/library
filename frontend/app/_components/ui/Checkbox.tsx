"use client";

import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export function Checkbox({
  className,
  ...props
}: Omit<InputHTMLAttributes<HTMLInputElement>, "type">) {
  return (
    <input
      {...props}
      type="checkbox"
      className={cn(
        "h-4 w-4 rounded border-[--color-border] bg-[--color-surface] text-[--color-accent]",
        "focus-visible:ring-2 focus-visible:ring-[--color-ring]",
        className,
      )}
    />
  );
}

