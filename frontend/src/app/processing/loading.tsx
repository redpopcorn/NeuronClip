import { Skeleton } from "@/components/ui/skeleton";

export default function ProcessingLoading() {
  return (
    <div className="space-y-4 px-6 py-8">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-12 rounded-xl" />
      ))}
    </div>
  );
}
