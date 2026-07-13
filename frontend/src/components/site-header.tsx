import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-black/40 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Badge
            variant="secondary"
            className="rounded-full bg-white/10 text-white"
          >
            Beta
          </Badge>
          <Link href="/" className="text-lg font-semibold text-white">
            ClipNeuron
          </Link>
        </div>
        <nav className="hidden items-center gap-6 text-sm text-white/70 md:flex">
          <a href="#product" className="transition hover:text-white">
            Product
          </a>
          <a href="#features" className="transition hover:text-white">
            Features
          </a>
          <a href="#pricing" className="transition hover:text-white">
            Pricing
          </a>
          <a href="#faq" className="transition hover:text-white">
            FAQ
          </a>
        </nav>
        <details className="md:hidden">
          <summary className="cursor-pointer text-sm text-white/70">
            Menu
          </summary>
          <div className="mt-2 flex flex-col gap-2 rounded-xl border border-white/10 bg-black/80 p-3 text-sm text-white/70">
            <a href="#product">Product</a>
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#faq">FAQ</a>
          </div>
        </details>
        <div className="flex items-center gap-3">
          <Link
            href="/signin"
            className={cn(
              buttonVariants({ variant: "ghost" }),
              "text-white/80 hover:text-white",
            )}
          >
            Sign in
          </Link>
          <Link
            href="/upload"
            className={cn(
              buttonVariants({ variant: "default" }),
              "rounded-full",
            )}
          >
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}
