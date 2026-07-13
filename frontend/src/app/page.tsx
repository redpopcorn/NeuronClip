"use client";

import Link from "next/link";
import { useState, useRef } from "react";

import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { SectionHeader } from "@/components/section-header";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const featureList = [
  {
    title: "Hook-first detection",
    body: "AI ranks openings by curiosity, emotion, and contrarianity to keep viewers locked in.",
  },
  {
    title: "Retention-aware trimming",
    body: "We reshape clip boundaries around complete thoughts and punchlines for higher watch time.",
  },
  {
    title: "Caption styling",
    body: "Word-level timing, bold emphasis, and safe-zone aware placement for mobile viewing.",
  },
  {
    title: "Viral scoring",
    body: "Score every candidate on hook, retention, and shareability before publishing.",
  },
  {
    title: "Team workflows",
    body: "Review, approve, and schedule clips with brand guardrails built in.",
  },
  {
    title: "Secure storage",
    body: "All media is encrypted and ready to export in platform-ready presets.",
  },
];

const pricing = [
  {
    name: "Starter",
    price: "$29",
    features: ["10 hours / month", "Auto captions", "Basic scoring"],
  },
  {
    name: "Studio",
    price: "$79",
    features: ["40 hours / month", "Advanced scoring", "Custom caption styles"],
    highlighted: true,
  },
  {
    name: "Agency",
    price: "$199",
    features: ["Unlimited hours", "Team review", "Priority render"],
  },
];

const faqs = [
  {
    q: "How fast are clips generated?",
    a: "A 60-minute podcast typically yields clips in 8-12 minutes depending on processing load.",
  },
  {
    q: "Can I customize captions?",
    a: "Yes. Choose from modern templates or create your own brand style presets.",
  },
  {
    q: "Is ClipNeuron just trimming?",
    a: "No. We optimize for hook strength, retention curves, and complete story arcs.",
  },
];

export default function HomePage() {
  const [isMuted, setIsMuted] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setIsMuted(videoRef.current.muted);
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="bg-[#08090D] text-white">
      <SiteHeader />

      <section className="relative overflow-hidden px-4 pb-24 pt-24">
        <div className="absolute left-1/2 top-[-120px] h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-blue-500/20 blur-[160px]" />
        <div className="mx-auto grid max-w-6xl gap-12 md:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="text-xs uppercase tracking-[0.4em] text-white/50">
              Clip. Post. Go viral.
            </div>
            <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
              Grow, earn, and go viral with ClipNeuron.
            </h1>
            <p className="text-lg text-white/70">
              Turn long-form podcasts into professional-grade clips with hook
              scoring, retention optimization, and studio-quality captions.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                href="/upload"
                className={cn(
                  buttonVariants({ variant: "default" }),
                  "rounded-full px-6",
                )}
              >
                Start Clipping
              </Link>
              <Link
                href="/dashboard"
                className={cn(
                  buttonVariants({ variant: "outline" }),
                  "rounded-full border-white/20 text-white",
                )}
              >
                View Dashboard
              </Link>
            </div>
            <div className="grid grid-cols-3 gap-4 pt-6 text-sm">
              {["$60M+ earned", "77k clips shipped", "200+ brands"].map(
                (stat) => (
                  <Card key={stat} className="bg-white/5">
                    <CardContent className="p-4 text-white/80">
                      {stat}
                    </CardContent>
                  </Card>
                ),
              )}
            </div>
          </div>
          <div className="relative">
            <div className="absolute -right-6 top-10 hidden h-64 w-40 rotate-6 rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 md:block" />
            <div className="relative mx-auto h-[520px] w-[280px] rounded-[2.5rem] border border-white/10 bg-black/70 p-4 shadow-2xl flex flex-col">
              <div className="flex items-center justify-between text-xs text-white/60 mb-3">
                <span>Clip preview</span>
                <Badge className="bg-white/10 text-white">Viral 92</Badge>
              </div>
              <div 
                className="relative flex-1 rounded-[2rem] overflow-hidden bg-black/40 border border-white/10 cursor-pointer group"
                onClick={togglePlay}
              >
                <video
                  ref={videoRef}
                  src="/hero_clip.mp4"
                  autoPlay
                  loop
                  muted={isMuted}
                  playsInline
                  className="w-full h-full object-cover"
                />
                
                {/* Play/Pause overlay indicator */}
                {!isPlaying && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <div className="rounded-full bg-white/10 p-4 backdrop-blur-sm border border-white/20">
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                  </div>
                )}

                {/* Bottom Overlay Controls */}
                <div className="absolute inset-x-2 bottom-2 flex flex-col gap-2 p-2 rounded-2xl bg-black/60 backdrop-blur-sm border border-white/5 opacity-90 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center justify-between">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMute();
                      }}
                      className="text-xs text-white/80 hover:text-white flex items-center gap-1 bg-white/10 px-2.5 py-1 rounded-full border border-white/10"
                    >
                      {isMuted ? (
                        <>
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 9.75L19.5 12m0 0l2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6L4.5 9H1.5v6h3l4.5 3.75V3.75z" />
                          </svg>
                          Unmute
                        </>
                      ) : (
                        <>
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
                          </svg>
                          Mute
                        </>
                      )}
                    </button>
                    <span className="text-[10px] text-white/50">Click to play/pause</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="product" className="px-4 pb-20">
        <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-white/5 p-10">
          <SectionHeader
            eyebrow="Product demo"
            title="Your entire clipping workflow, automated."
            description="Upload a full-length episode and walk away with a stack of ranked, ready-to-post clips."
          />
          <div className="mt-8 grid gap-6 md:grid-cols-3">
            {[
              "Upload → transcription",
              "Hook scoring → ranking",
              "Export → schedule",
            ].map((step) => (
              <Card key={step} className="bg-black/40">
                <CardContent className="p-6 text-white/80">{step}</CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {["AI score breakdown", "Clip editor", "Performance dashboard"].map(
              (label) => (
                <div
                  key={label}
                  className="h-40 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/10 p-4 text-sm text-white/60"
                >
                  {label}
                </div>
              ),
            )}
          </div>
        </div>
      </section>

      <section className="px-4 pb-20">
        <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-white/5 p-8">
          <div className="text-xs uppercase tracking-[0.3em] text-white/50">
            Trusted by modern studios
          </div>
          <div className="mt-6 grid grid-cols-2 gap-4 text-sm text-white/60 md:grid-cols-4">
            {["Signal Labs", "Arcade Media", "Notion House", "Stripeworks"].map(
              (brand) => (
                <div
                  key={brand}
                  className="rounded-full border border-white/10 bg-black/30 px-4 py-2 text-center"
                >
                  {brand}
                </div>
              ),
            )}
          </div>
        </div>
      </section>

      <section id="features" className="px-4 pb-24">
        <div className="mx-auto max-w-6xl">
          <SectionHeader
            eyebrow="Features"
            title="Built for viral performance."
            description="ClipNeuron balances storytelling, pacing, and visual polish so your shorts compete with human editors."
          />
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {featureList.map((feature) => (
              <Card key={feature.title} className="bg-white/5">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm text-white/70">{feature.body}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="px-4 pb-24">
        <div className="mx-auto max-w-6xl">
          <SectionHeader
            eyebrow="Pricing"
            title="Plans for every clipping cadence."
            description="Start lean, scale up when your pipeline demands higher volume."
          />
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {pricing.map((plan) => (
              <Card
                key={plan.name}
                className={`bg-white/5 ${plan.highlighted ? "border-blue-500/60" : "border-white/10"}`}
              >
                <CardContent className="p-6">
                  <div className="text-sm uppercase text-white/50">
                    {plan.name}
                  </div>
                  <div className="mt-3 text-3xl font-semibold">
                    {plan.price}
                  </div>
                  <ul className="mt-4 space-y-2 text-sm text-white/70">
                    {plan.features.map((feature) => (
                      <li key={feature}>• {feature}</li>
                    ))}
                  </ul>
                  <Button className="mt-6 w-full rounded-full">
                    Choose plan
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="faq" className="px-4 pb-24">
        <div className="mx-auto max-w-6xl">
          <SectionHeader
            eyebrow="FAQ"
            title="Answers before you clip."
            description="Everything you need to launch your clipping engine fast."
          />
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {faqs.map((faq) => (
              <Card key={faq.q} className="bg-white/5">
                <CardContent className="p-6">
                  <h3 className="font-semibold">{faq.q}</h3>
                  <p className="mt-2 text-sm text-white/70">{faq.a}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 pb-24">
        <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-gradient-to-br from-blue-500/20 to-purple-500/10 p-10 text-center">
          <h2 className="text-3xl font-semibold">Ready to ship viral clips?</h2>
          <p className="mt-3 text-white/70">
            Join creators who turn one episode into a month of high-retention
            shorts.
          </p>
          <Link
            href="/upload"
            className={cn(
              buttonVariants({ variant: "default" }),
              "mt-6 rounded-full px-6",
            )}
          >
            Start clipping
          </Link>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
