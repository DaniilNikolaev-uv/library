import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-blue-300/20 bg-primary/20 text-blue-200",
        secondary: "border-border/80 bg-surface-2/90 text-muted-foreground",
        outline: "border-border text-foreground",
        success: "border-emerald-900/50 bg-emerald-950/30 text-emerald-300",
        destructive: "border-red-900/50 bg-red-950/30 text-red-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
