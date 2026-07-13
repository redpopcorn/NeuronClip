export function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-3">
      <div className="text-xs uppercase tracking-[0.4em] text-white/50">
        {eyebrow}
      </div>
      <h2 className="text-3xl font-semibold text-white md:text-4xl">{title}</h2>
      <p className="max-w-2xl text-white/70">{description}</p>
    </div>
  );
}
