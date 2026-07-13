import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function EditorPage() {
  return (
    <AppShell
      title="Clip Editor"
      description="Fine-tune trims and caption styles."
    >
      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
        <Card className="bg-white/5">
          <CardContent className="p-6">
            <div className="aspect-[9/16] w-full rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-white/10" />
            <div className="mt-4 flex items-center justify-between text-sm text-white/70">
              <span>00:08</span>
              <span>00:52</span>
            </div>
            <div className="mt-3 h-2 rounded-full bg-white/10">
              <div className="h-2 w-2/3 rounded-full bg-blue-500" />
            </div>
            <div className="mt-4 grid gap-2 rounded-2xl border border-white/10 bg-black/30 p-3 text-xs text-white/60">
              <div className="flex items-center justify-between">
                <span>Hook segment</span>
                <span>0:08 → 0:22</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Punchline</span>
                <span>0:42 → 0:52</span>
              </div>
            </div>
          </CardContent>
        </Card>
        <div className="space-y-4">
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Caption style</h3>
              <Select>
                <SelectTrigger className="mt-4">
                  <SelectValue placeholder="Bold highlight" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bold">Bold highlight</SelectItem>
                  <SelectItem value="minimal">Minimal</SelectItem>
                  <SelectItem value="neon">Neon punch</SelectItem>
                </SelectContent>
              </Select>
              <Button className="mt-6 w-full">Apply style</Button>
            </CardContent>
          </Card>
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Trim controls</h3>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <Button
                  variant="outline"
                  className="border-white/20 text-white"
                >
                  -1s start
                </Button>
                <Button
                  variant="outline"
                  className="border-white/20 text-white"
                >
                  +1s start
                </Button>
                <Button
                  variant="outline"
                  className="border-white/20 text-white"
                >
                  -1s end
                </Button>
                <Button
                  variant="outline"
                  className="border-white/20 text-white"
                >
                  +1s end
                </Button>
              </div>
              <div className="mt-6 space-y-3">
                <Button className="w-full">Export clip</Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-white"
                >
                  Save draft
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
