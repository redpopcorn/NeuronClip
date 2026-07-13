import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function BillingPage() {
  return (
    <AppShell title="Billing" description="Manage your plan and usage.">
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="bg-white/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-white/60">Current plan</div>
                <div className="text-2xl font-semibold">Studio</div>
              </div>
              <Badge className="bg-blue-500/20 text-blue-200">Active</Badge>
            </div>
            <div className="mt-4 text-sm text-white/60">
              Next invoice: June 28 · $79
            </div>
            <Button className="mt-6">Upgrade plan</Button>
          </CardContent>
        </Card>
        <Card className="bg-white/5">
          <CardContent className="p-6">
            <h3 className="text-base font-semibold">Usage this month</h3>
            <div className="mt-4 space-y-3 text-sm text-white/70">
              <div className="flex justify-between">
                <span>Processing hours</span>
                <span>28 / 40</span>
              </div>
              <div className="h-2 rounded-full bg-white/10">
                <div className="h-2 w-2/3 rounded-full bg-emerald-500" />
              </div>
              <div className="flex justify-between">
                <span>Exports</span>
                <span>62 / 120</span>
              </div>
              <div className="h-2 rounded-full bg-white/10">
                <div className="h-2 w-1/2 rounded-full bg-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
