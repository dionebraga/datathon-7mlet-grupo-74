"use client";

import { motion } from "framer-motion";
import { Activity, Database, Radio, Satellite } from "lucide-react";
import type { Health, Policy } from "@/lib/types";

function Status({ on, label }: { on: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${
        on ? "border-success/30 bg-success/10 text-success" : "border-border bg-white/5 text-muted"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${on ? "bg-success" : "bg-muted"}`} />
      {label}
    </span>
  );
}

export function PolicyHeader({ health, policy }: { health?: Health; policy?: Policy }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card flex flex-col gap-4 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-7 sm:py-6"
    >
      <div className="flex items-center gap-3.5">
        <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-primary/15 text-primary-soft shadow-lg shadow-primary/10 sm:h-12 sm:w-12">
          <Satellite className="h-5 w-5 sm:h-6 sm:w-6" />
        </div>
        <div className="min-w-0">
          <div className="text-[0.66rem] font-bold uppercase tracking-[0.16em] text-primary-soft/80 sm:text-xs">
            FIAP Pós-Tech · 7MLET · Grupo 74
          </div>
          <h1 className="bg-gradient-to-r from-white via-primary-soft to-cyan-300 bg-clip-text text-xl font-extrabold leading-tight tracking-tight text-transparent sm:text-2xl">
            Adaptive Offers
          </h1>
          <p className="text-xs text-muted sm:text-sm">
            Decision Console · política ativa{" "}
            <b className="text-text">
              {policy ? `${policy.name}@${policy.version}` : "—"}
            </b>
          </p>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Status on={!!health?.policy_loaded} label="Política" />
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-white/5 px-3 py-1 text-xs font-bold text-muted">
          <Database className="h-3.5 w-3.5" /> Feature Store {health?.feature_store_materialized ? "✓" : "—"}
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-white/5 px-3 py-1 text-xs font-bold text-muted">
          {health?.status === "ok" ? <Radio className="h-3.5 w-3.5 text-success" /> : <Activity className="h-3.5 w-3.5" />}
          API {health?.status ?? "?"}
        </span>
      </div>
    </motion.header>
  );
}
