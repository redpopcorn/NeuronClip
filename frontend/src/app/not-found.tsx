import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#08090D] text-white">
      <h1 className="text-3xl font-semibold">Page not found</h1>
      <p className="text-sm text-white/60">
        The page you’re looking for doesn’t exist.
      </p>
      <Link href="/" className={cn(buttonVariants({ variant: "default" }))}>
        Back to home
      </Link>
    </div>
  );
}
