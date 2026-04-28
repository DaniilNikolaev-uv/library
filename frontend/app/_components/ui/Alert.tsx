import type { HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type Variant = "info" | "danger";

export function Alert({
  variant = "info",
  className,
  ...props
}: HTMLAttributes<HTMLDivElement> & { variant?: Variant }) {
  return (
    <div
      {...props}
      role="alert"
      className={cn(
        "rounded-md border px-3 py-2 text-sm",
        variant === "info" &&
          "border-[--color-border] bg-[--color-surface-2] text-[--color-text]",
        variant === "danger" &&
          "border-red-800/60 bg-red-950/40 text-red-200",
        className,
      )}
    />
  );
}

