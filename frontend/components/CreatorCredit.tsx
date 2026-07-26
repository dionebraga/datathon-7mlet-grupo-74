import { Linkedin, Package } from "lucide-react";

// Avatar is initials for now (placeholder until a real photo is provided) --
// swap the div below for a <Image src="/avatar.jpg" .../> once available.
export function CreatorCredit() {
  return (
    <div className="mt-3 flex flex-col items-center gap-2.5">
      <div className="flex items-center gap-2.5">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-primary/35 bg-gradient-to-br from-primary/20 to-cyan-400/20 text-xs font-extrabold text-primary-soft">
          DB
        </div>
        <div className="text-left">
          <div className="text-sm font-bold text-text">Dione Braga</div>
          <div className="text-xs text-muted">ML Engineer</div>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-2">
        <a
          href="https://www.linkedin.com/in/dionebraga/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-full border border-[#0A66C2]/35 bg-[#0A66C2]/15 px-3 py-1 text-xs font-bold text-[#5BA6FF] transition-colors hover:bg-[#0A66C2]/25"
        >
          <Linkedin className="h-3.5 w-3.5" /> LinkedIn
        </a>
        <a
          href="https://github.com/dionebraga/datathon-7mlet-grupo-74"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-full border border-success/30 bg-success/10 px-3 py-1 text-xs font-bold text-success transition-colors hover:bg-success/20"
        >
          <Package className="h-3.5 w-3.5" /> Repositório
        </a>
      </div>
    </div>
  );
}
