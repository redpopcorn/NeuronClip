import { Skeleton } from "@/components/ui/skeleton";

export default function EditorLoading() {
  return (
    <div className="grid gap-6 px-6 py-8 lg:grid-cols-[1.4fr_0.6fr]">
      <Skeleton className="h-[520px] rounded-3xl" />
      <div className="space-y-4">
        <Skeleton className="h-40 rounded-2xl" />
        <Skeleton className="h-48 rounded-2xl" />
      </div>
    </div>
  );
}
