import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";

export default function SettingsPage() {
  return (
    <AppShell title="Settings" description="Manage your workspace preferences.">
      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <Card className="bg-white/5">
          <CardContent className="space-y-4 p-6">
            <h3 className="text-base font-semibold">Profile</h3>
            <Input className="bg-black/30" placeholder="Name" />
            <Input className="bg-black/30" placeholder="Email" />
            <Button className="w-full">Save changes</Button>
          </CardContent>
        </Card>
        <Card className="bg-white/5">
          <CardContent className="space-y-4 p-6">
            <h3 className="text-base font-semibold">Notifications</h3>
            <div className="flex items-center justify-between text-sm text-white/70">
              <span>Processing complete</span>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between text-sm text-white/70">
              <span>Weekly performance</span>
              <Switch />
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
