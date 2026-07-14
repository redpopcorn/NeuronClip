"use client";

import Link from "next/link";
import { useState } from "react";
import { Copy, Check, Share2, X } from "lucide-react";
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
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const shareUrl = typeof window !== "undefined" ? window.location.origin : "https://neuron-clip-fsum.vercel.app";
  const shareText = "Create viral shorts from your podcasts with ClipNeuron!";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy!", err);
    }
  };

  const handleNativeShare = async () => {
    const nav = navigator as any;
    if (nav.share) {
      try {
        await nav.share({
          title: "ClipNeuron",
          text: shareText,
          url: shareUrl,
        });
      } catch (err) {
        console.error("Error sharing", err);
      }
    }
  };

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
              <Button
                variant="outline"
                className="border-white/20 text-white"
                onClick={() => setIsInviteOpen(true)}
              >
                Invite
              </Button>
              <Button className="rounded-full">New upload</Button>
            </div>
          </header>
          <main className="px-6 py-8">{children}</main>
        </div>
      </div>

      {/* Invite/Share Dialog Modal */}
      {isInviteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm transition-all duration-300">
          <div className="relative w-full max-w-md rounded-2xl border border-white/10 bg-[#0F111A]/95 p-6 shadow-2xl">
            
            {/* Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Share2 className="h-5 w-5 text-blue-400" />
                Invite Creators
              </h2>
              <button
                onClick={() => setIsInviteOpen(false)}
                className="rounded-full p-1.5 text-white/50 hover:bg-white/10 hover:text-white transition"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="mt-2 text-sm text-white/60">
              Share ClipNeuron with other creators and help them grow their audience with AI-powered clips.
            </p>

            {/* Share Link Input */}
            <div className="mt-6">
              <label className="text-xs font-medium text-white/40 uppercase tracking-wider">Share Link</label>
              <div className="mt-2 flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-2">
                <input
                  type="text"
                  readOnly
                  value={shareUrl}
                  className="flex-1 bg-transparent px-2 text-sm text-white/80 focus:outline-none"
                />
                <button
                  onClick={handleCopy}
                  className="flex h-9 items-center gap-1.5 rounded-lg bg-blue-600 px-3 text-xs font-semibold text-white hover:bg-blue-500 active:scale-95 transition"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Social Share Grid */}
            <div className="mt-6">
              <label className="text-xs font-medium text-white/40 uppercase tracking-wider">Share Directly</label>
              <div className="mt-3 grid grid-cols-2 gap-3">
                
                {/* WhatsApp */}
                <a
                  href={`https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + " " + shareUrl)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-emerald-500/10 p-3 text-sm font-medium text-emerald-300 hover:bg-emerald-500/20 active:scale-[0.98] transition"
                >
                  <span className="text-lg">💬</span>
                  WhatsApp
                </a>

                {/* Twitter / X */}
                <a
                  href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-blue-500/10 p-3 text-sm font-medium text-blue-300 hover:bg-blue-500/20 active:scale-[0.98] transition"
                >
                  <span className="text-lg">𝕏</span>
                  Twitter / X
                </a>

                {/* LinkedIn */}
                <a
                  href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-indigo-500/10 p-3 text-sm font-medium text-indigo-300 hover:bg-indigo-500/20 active:scale-[0.98] transition"
                >
                  <span className="text-lg">💼</span>
                  LinkedIn
                </a>

                {/* Facebook */}
                <a
                  href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2.5 rounded-xl border border-white/5 bg-sky-600/10 p-3 text-sm font-medium text-sky-400 hover:bg-sky-600/20 active:scale-[0.98] transition"
                >
                  <span className="text-lg">👥</span>
                  Facebook
                </a>

              </div>
            </div>

            {/* Native OS Share Sheet */}
            {typeof navigator !== "undefined" && !!(navigator as any).share && (
              <button
                onClick={handleNativeShare}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 p-3 text-sm font-medium text-white/80 hover:bg-white/10 active:scale-[0.98] transition"
              >
                <Share2 className="h-4 w-4" />
                More Share Options
              </button>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
