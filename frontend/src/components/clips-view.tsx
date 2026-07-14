"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { API_BASE } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Clip = {
  title?: string;
  text?: string;
  scores?: { overall?: number };
  download_url?: string;
  clip_id?: string;
};

type ClipsResponse = {
  clips?: Clip[];
};

export function ClipsView() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project") ?? "";
  const [clips, setClips] = useState<Clip[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      return;
    }
    const fetchClips = async () => {
      const response = await fetch(`${API_BASE}/project/${projectId}/clips`);
      if (!response.ok) {
        setError("Clips not ready yet.");
        return;
      }
      const data = (await response.json()) as ClipsResponse;
      setClips(data.clips ?? []);
      setError(null);
    };
    void fetchClips();
  }, [projectId]);

  if (!projectId) {
    return (
      <div className="text-sm text-white/60">
        No project selected. Upload a video to view clips.
      </div>
    );
  }

  if (error) {
    return <div className="text-sm text-rose-200">{error}</div>;
  }

  if (!clips.length) {
    return <div className="text-sm text-white/60">Loading clips...</div>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {clips.map((clip, index) => (
        <Card key={clip.clip_id ?? index} className="bg-white/5">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  {clip.title ?? `Clip ${index + 1}`}
                </h3>
                <p className="text-sm text-white/60 line-clamp-2">
                  {clip.text ?? ""}
                </p>
              </div>
              <Badge className="bg-emerald-500/20 text-emerald-200">
                {Math.round(clip.scores?.overall ?? 0)}
              </Badge>
            </div>
            <div className="mt-4 overflow-hidden rounded-2xl border border-white/10 bg-black">
              {clip.download_url ? (
                <video
                  src={`${API_BASE}${clip.download_url}`}
                  controls
                  playsInline
                  className="w-full h-48 object-cover"
                />
              ) : (
                <div className="h-48 bg-gradient-to-br from-white/5 to-white/10" />
              )}
            </div>
            <div className="mt-4 flex items-center justify-between text-sm text-white/60">
              <span>Auto captions · 9:16</span>
              <span>Ready</span>
            </div>
            <div className="mt-4 flex gap-3">
              <a
                href={
                  clip.download_url ? `${API_BASE}${clip.download_url}` : "#"
                }
                className={cn(buttonVariants({ variant: "default" }), "flex-1")}
                aria-disabled={!clip.download_url}
              >
                Download
              </a>
              <Button
                variant="outline"
                className="flex-1 border-white/20 text-white"
              >
                Regenerate
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
