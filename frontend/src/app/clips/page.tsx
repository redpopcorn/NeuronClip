import { AppShell } from "@/components/app-shell";
import { ClipsView } from "@/components/clips-view";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function ClipsPage() {
  return (
    <AppShell title="Generated Clips" description="Review, score, and export.">
      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <Input
          placeholder="Search clips"
          className="max-w-sm bg-black/30"
          aria-label="Search clips"
        />
        <div className="flex gap-3">
          <Select>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Sort by score" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="score">Viral score</SelectItem>
              <SelectItem value="duration">Duration</SelectItem>
              <SelectItem value="recent">Most recent</SelectItem>
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All clips</SelectItem>
              <SelectItem value="ready">Ready</SelectItem>
              <SelectItem value="draft">Drafts</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <ClipsView />
    </AppShell>
  );
}
