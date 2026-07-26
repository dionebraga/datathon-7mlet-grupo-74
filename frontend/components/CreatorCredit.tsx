import Image from "next/image";
import { Linkedin, Package } from "lucide-react";

export function CreatorCredit() {
  return (
    <div className="mt-3 flex flex-col items-center gap-2.5">
      <div className="flex items-center gap-2.5">
        <Image
          src="/avatar.png"
          alt="Dione Braga"
          width={36}
          height={36}
          className="h-9 w-9 shrink-0 rounded-full border border-primary/35 object-cover object-top"
        />
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
