import { AppShell } from "@/components/app-shell";
import { UploadForm } from "@/components/upload-form";
import { Card, CardContent } from "@/components/ui/card";

export default function UploadPage() {
  return (
    <AppShell
      title="Upload"
      description="Drop a full episode to start clipping."
    >
      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <Card className="bg-white/5">
          <CardContent className="p-8">
            <UploadForm />
          </CardContent>
        </Card>
        <Card className="bg-white/5">
          <CardContent className="p-6">
            <h3 className="text-base font-semibold">File validation</h3>
            <ul className="mt-4 space-y-3 text-sm text-white/70">
              <li>✓ Resolution: 1920x1080</li>
              <li>✓ Audio track detected</li>
              <li>✓ Duration: 61:12</li>
              <li>✓ Language: English</li>
              <li>✓ File size: 2.4GB / 4GB</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
