import type { HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type Variant = "default" | "muted" | "accent";

export function Badge({
  variant = "default",
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { variant?: Variant }) {
  return (
    <span
      {...props}
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        variant === "default" &&
          "border-[--color-border] bg-[--color-surface] text-[--color-text]",
        variant === "muted" &&
          "border-[--color-border] bg-[--color-surface-2] text-[--color-muted]",
        variant === "accent" &&
          "border-blue-500/30 bg-blue-500/15 text-blue-200",
        className,
      )}
    />
  );
}

