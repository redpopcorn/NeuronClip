export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-black/60">
      <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-4 py-10 text-sm text-white/60 md:flex-row">
        <div>
          <div className="text-base font-semibold text-white">ClipNeuron</div>
          <p className="mt-2 max-w-sm">
            Turn long-form podcasts into viral clips with AI that mimics
            professional editors.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-8 md:grid-cols-3">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-white/40">
              Product
            </div>
            <ul className="mt-3 space-y-2">
              <li>Clips</li>
              <li>Editor</li>
              <li>Analytics</li>
            </ul>
          </div>
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-white/40">
              Company
            </div>
            <ul className="mt-3 space-y-2">
              <li>Blog</li>
              <li>Careers</li>
              <li>Contact</li>
            </ul>
          </div>
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-white/40">
              Legal
            </div>
            <ul className="mt-3 space-y-2">
              <li>Privacy</li>
              <li>Terms</li>
              <li>Security</li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  );
}
