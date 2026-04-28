"use client";

import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

export function Button({
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
}) {
  return (
    <button
      {...props}
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--color-ring]",
        "disabled:pointer-events-none disabled:opacity-60",
        size === "sm" ? "h-8 px-3" : "h-9 px-4",
        variant === "primary" &&
          "bg-[--color-accent] text-[--color-accent-foreground] hover:bg-blue-500",
        variant === "secondary" &&
          "border border-[--color-border] bg-[--color-surface] text-[--color-text] hover:bg-[--color-surface-2]",
        variant === "ghost" &&
          "text-[--color-muted] hover:bg-[--color-surface-2] hover:text-[--color-text]",
        variant === "danger" &&
          "border border-red-800/50 bg-red-950/40 text-red-200 hover:bg-red-950/70",
        className,
      )}
    />
  );
}

