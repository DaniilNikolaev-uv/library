"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-semibold transition-all duration-200 disabled:pointer-events-none disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
  {
    variants: {
      variant: {
        default:
          "border border-blue-300/20 bg-primary text-primary-foreground shadow-lg shadow-blue-950/20 hover:-translate-y-0.5 hover:brightness-110",
        secondary:
          "border border-border/90 bg-surface/90 text-foreground shadow-sm shadow-black/10 hover:-translate-y-0.5 hover:bg-surface-2",
        ghost: "text-muted-foreground hover:bg-surface-2/80 hover:text-foreground",
        destructive:
          "border border-red-800/50 bg-red-950/40 text-red-200 hover:-translate-y-0.5 hover:bg-red-950/70",
        outline: "border border-border bg-transparent hover:-translate-y-0.5 hover:bg-surface-2",
      },
      size: {
        sm: "h-8 px-3",
        default: "h-9 px-4 py-2",
        lg: "h-10 px-5",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
