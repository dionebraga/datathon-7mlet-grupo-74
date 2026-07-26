// Mirrors the FastAPI contracts (src/adaptive_offers/api/schemas.py).

export interface Health {
  status: string;
  policy_loaded: boolean;
  feature_store_materialized: boolean;
  version: string | null;
}

export interface Policy {
  name: string;
  version: string;
  trained_on: string;
  metrics: Record<string, number | string>;
}

export interface Offer {
  offer_id: string;
  name: string;
  category: string;
  margin: number;
  suitability_tier: string;
}

export interface Reason {
  code: string;
  description: string;
}

export interface Decision {
  decision_id: string;
  ts: string;
  client_event_id: string | null;
  arm_id: string;
  arm_name: string;
  score: number;
  expected_reward: number;
  explored: boolean;
  policy_name: string;
  policy_version: string;
  eligible_arms: string[];
  reason_codes: string[];
  reasons: Reason[];
  estimates: Record<string, number>;
  scores: Record<string, number>;
  segment_id: string;
  segment_label: string;
  channel_id: string;
  channel_label: string;
  nba_action: string;
  nba_headline: string;
  nba_message: string;
  nba_cta: string;
  protected_groups: Record<string, string>;
}

export interface PolicyMetrics {
  policy: string;
  cumulative_reward: number;
  reward_per_1k: number;
  cumulative_regret: number;
  regret_ratio: number;
  conversion_rate: number;
  exploration_rate: number;
  lift_vs_baseline_pct: number | null;
}

export interface AuditEntry {
  decision_id: string;
  ts: string;
  arm_id: string;
  arm_name: string | null;
  score: number | null;
  expected_reward: number | null;
  explored: boolean | null;
  policy_name: string | null;
  policy_version: string | null;
  reason_codes: string[];
}

export interface AuditSummary {
  total_decisions: number;
  entries: AuditEntry[];
}

export interface AssistantAnswer {
  answer: string;
  provider: string;
  citations: { source: string; score: number; text: string }[];
}

export interface ContextInput {
  age: number;
  contact: "cellular" | "telephone";
  poutcome: "nonexistent" | "failure" | "success";
  euribor3m: number;
  default: "no" | "yes" | "unknown";
  loan: "no" | "yes" | "unknown";
  previously_contacted: number;
}
