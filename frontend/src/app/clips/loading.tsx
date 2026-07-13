import { Skeleton } from "@/components/ui/skeleton";

export default function ClipsLoading() {
  return (
    <div className="grid gap-6 px-6 py-8 md:grid-cols-2">
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="h-64 rounded-2xl" />
      ))}
    </div>
  );
}
