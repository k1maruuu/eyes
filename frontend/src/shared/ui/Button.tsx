import { clsx } from "clsx";
import type { ButtonHTMLAttributes } from "react";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={clsx(
        "rounded-xl px-4 py-2 text-sm font-medium shadow-sm border border-slate-200 bg-white hover:bg-slate-50 active:scale-[0.99] disabled:opacity-50",
        className
      )}
    />
  );
}
