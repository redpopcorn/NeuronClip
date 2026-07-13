"use client";

import Link from "next/link";
import { Menu } from "lucide-react";

import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

const navItems = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Upload", href: "/upload" },
  { label: "Processing", href: "/processing" },
  { label: "Clips", href: "/clips" },
  { label: "Editor", href: "/editor" },
  { label: "Billing", href: "/billing" },
  { label: "Settings", href: "/settings" },
];

export function MobileNav() {
  return (
    <Sheet>
      <SheetTrigger
        render={
          <Button variant="ghost" size="icon" aria-label="Open navigation" />
        }
      >
        <Menu className="h-5 w-5" />
      </SheetTrigger>
      <SheetContent side="left" className="bg-[#0B0B0F] text-white">
        <div className="mt-8 space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block rounded-lg px-3 py-2 text-sm text-white/80 hover:bg-white/10"
            >
              {item.label}
            </Link>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}
