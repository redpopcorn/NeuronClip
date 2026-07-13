import { Skeleton } from "@/components/ui/skeleton";

export default function SignInLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#08090D] px-4">
      <Skeleton className="h-80 w-full max-w-md rounded-2xl" />
    </div>
  );
}
