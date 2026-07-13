import { AppShell } from "@/components/app-shell";
import { ProcessingClient } from "@/components/processing-client";
import { Card, CardContent } from "@/components/ui/card";

export default function ProcessingPage() {
  return (
    <AppShell title="Processing" description="Live progress for Episode 118.">
      <Card className="bg-white/5">
        <CardContent className="p-8">
          <div className="mb-6 flex items-center justify-between text-sm text-white/60">
            <span>Estimated time remaining: 3m 12s</span>
            <span>52% complete</span>
          </div>
          <ProcessingClient />
          <div className="mt-8">
            <ProcessingClient />
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
