import { AppShell } from "@/components/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const projects = [
  {
    title: "Founder Stories Ep. 118",
    clips: 12,
    status: "Ready",
  },
  {
    title: "Growth Signal Live",
    clips: 8,
    status: "Processing",
  },
  {
    title: "Edge Cases Podcast",
    clips: 15,
    status: "Drafts",
  },
];

const uploads = [
  { name: "Episode_118.mp4", date: "2 hours ago" },
  { name: "Episode_119.mp4", date: "Yesterday" },
  { name: "Special_QA.mp4", date: "2 days ago" },
];

const stats = [
  { label: "Total watch time", value: "312h" },
  { label: "Avg. viral score", value: "88.6" },
  { label: "Clips published", value: "74" },
];

export default function DashboardPage() {
  return (
    <AppShell
      title="Dashboard"
      description="Your clip performance at a glance."
    >
      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <section className="grid gap-4 md:grid-cols-3">
            {stats.map((stat) => (
              <Card key={stat.label} className="bg-white/5">
                <CardContent className="p-6">
                  <div className="text-xs uppercase text-white/50">
                    {stat.label}
                  </div>
                  <div className="mt-3 text-2xl font-semibold">
                    {stat.value}
                  </div>
                </CardContent>
              </Card>
            ))}
          </section>

          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Projects</h2>
              <Badge className="bg-white/10 text-white">3 Active</Badge>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {projects.map((project) => (
                <Card key={project.title} className="bg-white/5">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-base font-semibold">
                          {project.title}
                        </div>
                        <div className="text-sm text-white/60">
                          {project.clips} clips
                        </div>
                      </div>
                      <Badge
                        className={
                          project.status === "Ready"
                            ? "bg-emerald-500/20 text-emerald-200"
                            : "bg-white/10 text-white"
                        }
                      >
                        {project.status}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        </div>

        <section className="space-y-4">
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Recent uploads</h3>
              <ul className="mt-4 space-y-3 text-sm text-white/70">
                {uploads.map((upload) => (
                  <li key={upload.name} className="flex justify-between">
                    <span>{upload.name}</span>
                    <span>{upload.date}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Usage</h3>
              <p className="mt-2 text-sm text-white/60">
                28 hours used · 12 hours remaining
              </p>
              <div className="mt-4 h-2 rounded-full bg-white/10">
                <div className="h-2 w-2/3 rounded-full bg-blue-500" />
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Empty state</h3>
              <p className="mt-2 text-sm text-white/60">
                No approved clips yet. Upload a new episode to generate your
                first batch.
              </p>
            </CardContent>
          </Card>
          <Card className="bg-white/5">
            <CardContent className="p-6">
              <h3 className="text-base font-semibold">Error state</h3>
              <p className="mt-2 text-sm text-rose-200">
                We couldn’t load one project. Try refreshing or contact support.
              </p>
            </CardContent>
          </Card>
        </section>
      </div>
    </AppShell>
  );
}
