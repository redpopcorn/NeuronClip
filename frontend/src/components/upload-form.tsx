"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { API_BASE } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

const MAX_SIZE = 4 * 1024 * 1024 * 1024;
const ACCEPTED = ["video/mp4", "video/quicktime", "audio/wav", "audio/x-wav"];

export function UploadForm() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [progress, setProgress] = useState(0);
  const [filename, setFilename] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const [musicEnabled, setMusicEnabled] = useState(true);
  const [musicCategory, setMusicCategory] = useState("auto");
  const [duckingStrength, setDuckingStrength] = useState("medium");

  const [task, setTask] = useState("transcribe");
  const [cropEnabled, setCropEnabled] = useState(true);

  const handleFile = async (file: File) => {
    if (!ACCEPTED.includes(file.type)) {
      toast.error("Unsupported format", {
        description: "Upload MP4, MOV, or WAV files.",
      });
      return;
    }
    if (file.size > MAX_SIZE) {
      toast.error("File too large", {
        description: "Max size is 4GB.",
      });
      return;
    }
    setFilename(file.name);
    setUploading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append("video", file);
    formData.append("music_enabled", String(musicEnabled));
    formData.append("music_category", musicCategory === "auto" ? "" : musicCategory);
    formData.append("task", task);
    formData.append("crop_enabled", String(cropEnabled));

    let ratio = 8.0;
    let threshold = 0.03;
    if (duckingStrength === "low") {
      ratio = 4.0;
      threshold = 0.05;
    } else if (duckingStrength === "high") {
      ratio = 16.0;
      threshold = 0.02;
    } else if (duckingStrength === "none") {
      ratio = 1.0;
      threshold = 1.0;
    }
    formData.append("ducking_ratio", String(ratio));
    formData.append("ducking_threshold", String(threshold));

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      setProgress(100);
      const data = await response.json();
      toast.success("Upload started", {
        description: "Processing has begun.",
      });
      router.push(`/processing?project=${data.project_id}`);
    } catch (error) {
      toast.error("Upload failed", {
        description: "Please try again.",
      });
      setUploading(false);
      setProgress(0);
    }
  };

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) {
      void handleFile(file);
    }
  };

  return (
    <div className="space-y-6">
      <div
        className="flex h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-white/20 bg-white/5 text-center focus-visible:ring-2 focus-visible:ring-blue-500"
        role="button"
        tabIndex={0}
        aria-label="Upload video"
        onDragOver={(event) => event.preventDefault()}
        onDrop={onDrop}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            inputRef.current?.click();
          }
        }}
      >
        <div className="text-lg font-semibold">Drag and drop video</div>
        <p className="mt-2 text-sm text-white/60">
          MP4, MOV, or WAV up to 4GB. We auto-detect scenes and speakers.
        </p>
        <Button
          className="mt-6 rounded-full"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Browse files"}
        </Button>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={ACCEPTED.join(",")}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              void handleFile(file);
            }
          }}
        />
        {filename && (
          <div className="mt-6 w-full max-w-sm text-left text-sm text-white/60">
            <div className="flex justify-between">
              <span>{filename}</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="mt-3" />
          </div>
        )}
      </div>

      <Separator className="bg-white/10" />

      {/* Video & Transcription Settings */}
      <div className="space-y-4 text-left">
        <h4 className="text-sm font-medium text-white/80">Video & Transcription Settings</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-xs text-white/50">Transcription Target Language</label>
            <Select
              disabled={uploading}
              value={task}
              onValueChange={(val) => setTask(val ?? "transcribe")}
            >
              <SelectTrigger className="bg-black/30 border-white/10 text-white">
                <SelectValue placeholder="Original Language" />
              </SelectTrigger>
              <SelectContent className="bg-[#12131a] border-white/10 text-white">
                <SelectItem value="transcribe">Original Language (e.g. Hindi/Urdu/English)</SelectItem>
                <SelectItem value="translate">English Only (Auto-Translate to English)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-white/50">Video Editing Style</label>
            <Select
              disabled={uploading}
              value={cropEnabled ? "crop" : "minimal"}
              onValueChange={(val) => setCropEnabled(val === "crop")}
            >
              <SelectTrigger className="bg-black/30 border-white/10 text-white">
                <SelectValue placeholder="Smart Crop" />
              </SelectTrigger>
              <SelectContent className="bg-[#12131a] border-white/10 text-white">
                <SelectItem value="crop">Smart Portrait Crop (9:16 with Speaker Tracking)</SelectItem>
                <SelectItem value="minimal">Minimal Edit (Keep original resolution/aspect ratio + captions)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Separator className="bg-white/10" />

      {/* Audio Settings */}
      <div className="space-y-4 text-left">
        <h4 className="text-sm font-medium text-white/80">Background Audio Settings</h4>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-xs text-white/50">Enable Background Music</label>
            <div className="flex items-center h-10">
              <Switch
                checked={musicEnabled}
                onCheckedChange={setMusicEnabled}
                disabled={uploading}
              />
              <span className="ml-3 text-sm text-white/80">
                {musicEnabled ? "On" : "Off"}
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-white/50">Music Track Category</label>
            <Select
              disabled={!musicEnabled || uploading}
              value={musicCategory}
              onValueChange={(val) => setMusicCategory(val ?? "auto")}
            >
              <SelectTrigger className="bg-black/30 border-white/10 text-white">
                <SelectValue placeholder="Auto-detect" />
              </SelectTrigger>
              <SelectContent className="bg-[#12131a] border-white/10 text-white">
                <SelectItem value="auto">Auto-detect (AI)</SelectItem>
                <SelectItem value="podcast">Podcast Chill</SelectItem>
                <SelectItem value="upbeat">Upbeat / Energetic</SelectItem>
                <SelectItem value="tension">Tension / Drama</SelectItem>
                <SelectItem value="inspirational">Inspirational</SelectItem>
                <SelectItem value="gaming">Gaming Beat</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-white/50">Audio Ducking Strength</label>
            <Select
              disabled={!musicEnabled || uploading}
              value={duckingStrength}
              onValueChange={(val) => setDuckingStrength(val ?? "medium")}
            >
              <SelectTrigger className="bg-black/30 border-white/10 text-white">
                <SelectValue placeholder="Medium" />
              </SelectTrigger>
              <SelectContent className="bg-[#12131a] border-white/10 text-white">
                <SelectItem value="none">Disabled (No Ducking)</SelectItem>
                <SelectItem value="low">Low Ducking</SelectItem>
                <SelectItem value="medium">Medium Ducking</SelectItem>
                <SelectItem value="high">High Ducking</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    </div>
  );
}
