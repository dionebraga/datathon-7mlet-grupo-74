"use client";

import { Scale } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardTitle } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { pct, POLICY_LABEL } from "@/lib/utils";
import type { PolicyMetrics } from "@/lib/types";

// Consumes GET /metrics -- exposed by the API since the start but never
// rendered anywhere on the frontend (the KPI cards only show the single
// active policy). This is the only place a user can compare all policies
// side by side without opening the Streamlit dashboard.
export function PolicyComparison({ activePolicy }: { activePolicy?: string }) {
  const [rows, setRows] = useState<PolicyMetrics[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .metrics()
      .then((m) => setRows([...m].sort((a, b) => b.reward_per_1k - a.reward_per_1k)))
      .catch((e) => setError(e instanceof Error ? e.message : "Falha ao carregar métricas"));
  }, []);

  if (error) return null;
  if (!rows) {
    return (
      <Card>
        <CardTitle icon={<Scale className="h-4 w-4 text-primary-soft" />}>Comparação de políticas</CardTitle>
        <div className="h-40 animate-pulse rounded-xl bg-white/5" />
      </Card>
    );
  }

  const chartData = rows.map((r) => ({
    name: POLICY_LABEL[r.policy] ?? r.policy,
    value: r.reward_per_1k,
    active: r.policy === activePolicy,
  }));

  return (
    <Card>
      <CardTitle icon={<Scale className="h-4 w-4 text-primary-soft" />}>Comparação de políticas</CardTitle>
      <p className="-mt-1 mb-3 text-xs text-muted">
        Reward por 1k impressões, todas as políticas simuladas · a ativa em destaque
      </p>
      <ResponsiveContainer width="100%" height={Math.max(160, chartData.length * 40)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 40, top: 4, bottom: 4 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            tick={{ fill: "#a1a1aa", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.04)" }}
            contentStyle={{
              background: "#0a0a0a",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 12,
              color: "#ededed",
            }}
            formatter={(v: number) => [`R$ ${v.toFixed(0)}`, "reward / 1k"]}
          />
          <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={20}>
            {chartData.map((d, i) => (
              <Cell key={i} fill={d.active ? "#34d399" : "#0070f3"} fillOpacity={d.active ? 1 : 0.6} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-muted">
              <th className="pb-2 pr-3 font-semibold">Política</th>
              <th className="pb-2 pr-3 font-semibold">Conversão</th>
              <th className="pb-2 pr-3 font-semibold">Regret</th>
              <th className="pb-2 pr-3 font-semibold">Exploração</th>
              <th className="pb-2 font-semibold">Lift</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.policy} className="border-t border-border">
                <td className="py-2 pr-3 font-bold text-text">
                  {POLICY_LABEL[r.policy] ?? r.policy}
                  {r.policy === activePolicy && (
                    <span className="ml-1.5 rounded-full bg-success/15 px-1.5 py-0.5 text-[0.6rem] font-bold text-success">
                      ativa
                    </span>
                  )}
                </td>
                <td className="py-2 pr-3 text-muted">{pct(r.conversion_rate)}</td>
                <td className="py-2 pr-3 text-muted">{pct(r.regret_ratio)}</td>
                <td className="py-2 pr-3 text-muted">{pct(r.exploration_rate)}</td>
                <td className={`py-2 font-semibold ${(r.lift_vs_baseline_pct ?? 0) >= 0 ? "text-success" : "text-danger"}`}>
                  {r.lift_vs_baseline_pct != null ? `${r.lift_vs_baseline_pct >= 0 ? "+" : ""}${r.lift_vs_baseline_pct.toFixed(0)}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
