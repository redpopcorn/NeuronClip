import Link from "next/link";

import { MobileNav } from "@/components/mobile-nav";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
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

export function AppShell({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#0B0B0F] text-white">
      <div className="flex">
        <aside className="hidden min-h-screen w-64 flex-col border-r border-white/10 bg-[#0D0F14] p-6 md:flex">
          <div className="flex items-center justify-between">
            <div className="text-lg font-semibold">ClipNeuron</div>
            <Badge variant="secondary" className="bg-white/10 text-white">
              Beta
            </Badge>
          </div>
          <nav className="mt-10 space-y-2 text-sm text-white/70">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block rounded-lg px-3 py-2 transition hover:bg-white/10 hover:text-white"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="mt-auto flex items-center gap-3 rounded-lg bg-white/5 p-3">
            <Avatar className="h-9 w-9">
              <AvatarFallback>AK</AvatarFallback>
            </Avatar>
            <div>
              <div className="text-sm font-medium">Aria Kim</div>
              <div className="text-xs text-white/50">Creator Pro</div>
            </div>
          </div>
        </aside>
        <div className="flex-1">
          <header className="flex items-center justify-between border-b border-white/10 px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="md:hidden">
                <MobileNav />
              </div>
              <div>
                <h1 className="text-2xl font-semibold">{title}</h1>
                {description && (
                  <p className="text-sm text-white/60">{description}</p>
                )}
              </div>
            </div>
            <div className="hidden items-center gap-3 md:flex">
              <Button variant="outline" className="border-white/20 text-white">
                Invite
              </Button>
              <Button className="rounded-full">New upload</Button>
            </div>
          </header>
          <main className="px-6 py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
