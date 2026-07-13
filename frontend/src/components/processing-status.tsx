"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { API_BASE } from "@/lib/api";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type ProjectStatus = {
  status?: "processing" | "completed" | "failed";
  progress?: number;
  stage?: string;
  error?: string;
};

const orderedStages = [
  "transcription",
  "candidate_generation",
  "boundary_optimization",
  "rendering",
  "ranking",
  "completed",
];

const labels: Record<string, string> = {
  transcription: "Transcribing audio",
  candidate_generation: "Detecting hooks",
  boundary_optimization: "Optimizing boundaries",
  rendering: "Rendering captions",
  ranking: "Ranking clips",
  completed: "Completed",
};

export function ProcessingStatus({ projectId }: { projectId: string }) {
  const [project, setProject] = useState<ProjectStatus>({
    progress: 0,
    status: "processing",
    stage: "transcription",
  });

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const poll = async () => {
      const response = await fetch(`${API_BASE}/project/${projectId}`);
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as ProjectStatus;
      setProject({
        progress: data.progress ?? 0,
        status: data.status ?? "processing",
        stage: data.stage ?? "transcription",
        error: data.error,
      });
    };

    void poll();
    interval = setInterval(poll, 2500);

    return () => clearInterval(interval);
  }, [projectId]);

  const currentIndex = useMemo(() => {
    const idx = orderedStages.indexOf(project.stage ?? "transcription");
    return idx === -1 ? 0 : idx;
  }, [project.stage]);

  return (
    <div className="space-y-8">
      <div className="mt-6 flex items-center justify-between text-sm text-white/60">
        <span>
          {project.status === "completed"
            ? "Processing complete"
            : "Processing..."}
        </span>
        <span>{project.progress}%</span>
        {project.status === "completed" && (
          <Link
            href={`/clips?project=${projectId}`}
            className={cn(buttonVariants({ size: "sm" }))}
          >
            View clips
          </Link>
        )}
        {project.status === "failed" && (
          <span className="text-rose-200">
            {project.error ?? "Processing failed"}
          </span>
        )}
      </div>

      <div className="space-y-6">
        {orderedStages.slice(0, 5).map((stage, index) => {
          const done = project.status === "completed" || index < currentIndex;
          const active =
            project.status === "processing" && index === currentIndex;
          const failed = project.status === "failed" && index === currentIndex;

          return (
            <div key={stage} className="flex items-start gap-4">
              <div
                className={cn(
                  "mt-1 h-3 w-3 rounded-full",
                  done && "bg-emerald-400",
                  active && "animate-pulse bg-blue-400",
                  failed && "bg-rose-400",
                  !done && !active && !failed && "bg-white/20",
                )}
              />
              <div className="flex-1">
                <div className="text-sm font-medium text-white">
                  {index + 1}. {labels[stage]}
                </div>
                <p className="text-xs text-white/60">
                  {failed
                    ? (project.error ?? "Failed")
                    : done
                      ? "Completed"
                      : active
                        ? "In progress"
                        : "Queued"}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
