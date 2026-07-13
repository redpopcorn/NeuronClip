"use client";

import { useSearchParams } from "next/navigation";

import { ProcessingStatus } from "@/components/processing-status";

export function ProcessingClient() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get("project") ?? "";

  if (!projectId) {
    return (
      <div className="text-sm text-white/60">
        No project selected. Upload a video to begin.
      </div>
    );
  }

  return <ProcessingStatus projectId={projectId} />;
}
