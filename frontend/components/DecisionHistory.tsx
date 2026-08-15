"use client";

import { History, Search, Target } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardTitle } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { brl } from "@/lib/utils";
import type { AuditEntry } from "@/lib/types";

// Consumes GET /audit -- the API's decision log was only ever surfaced in the
// Streamlit dashboard's "live feed"; the frontend had no history view at all,
// just whatever the explorer form last returned. Polls every 25s so newly
// logged decisions (from anywhere hitting /decide) show up without a reload.
export function DecisionHistory() {
  const [entries, setEntries] = useState<AuditEntry[] | null>(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = () =>
      api
        .audit(8)
        .then((r) => {
          if (cancelled) return;
          setEntries(r.entries);
          setTotal(r.total_decisions);
        })
        .catch((e) => !cancelled && setError(e instanceof Error ? e.message : "Falha ao carregar auditoria"));
    load();
    const id = setInterval(load, 25_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (error) return null;

  const explored = entries?.filter((e) => e.explored).length ?? 0;

  return (
    <Card>
      <div className="flex items-center justify-between">
        <CardTitle icon={<History className="h-4 w-4 text-primary-soft" />}>Histórico de decisões</CardTitle>
        {total > 0 && <span className="text-xs text-muted">{total} no log</span>}
      </div>

      {!entries ? (
        <div className="h-40 animate-pulse rounded-xl bg-white/5" />
      ) : entries.length === 0 ? (
        <p className="text-sm text-muted">Nenhuma decisão registrada ainda — use o explorador acima.</p>
      ) : (
        <>
          <div className="mb-3 flex items-center gap-3 text-xs text-muted">
            <span className="inline-flex items-center gap-1">
              <Search className="h-3 w-3 text-warning" /> {explored} exploração
            </span>
            <span className="inline-flex items-center gap-1">
              <Target className="h-3 w-3 text-success" /> {entries.length - explored} explotação
            </span>
          </div>
          <ul className="max-h-72 space-y-1.5 overflow-y-auto pr-1">
            {/* O log é append-only e histórico: registros gravados antes da
                correção do gerador de IDs compartilham `decision_id`. A posição
                desambigua sem esconder o dado antigo. */}
            {entries.map((e, i) => (
              <li
                key={`${e.decision_id}#${i}`}
                className="flex items-center justify-between gap-2 rounded-lg border border-border bg-white/[0.03] px-3 py-2 text-xs"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <span
                    className={`h-1.5 w-1.5 shrink-0 rounded-full ${e.explored ? "bg-warning" : "bg-success"}`}
                  />
                  <span className="truncate font-semibold text-text">{e.arm_name ?? e.arm_id}</span>
                  <span className="shrink-0 text-muted">{new Date(e.ts).toLocaleTimeString("pt-BR")}</span>
                </div>
                <span className="shrink-0 font-bold text-primary-soft">
                  {e.expected_reward != null ? brl(e.expected_reward) : "—"}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </Card>
  );
}
