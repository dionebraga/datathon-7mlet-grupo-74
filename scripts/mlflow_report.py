"""Leitor de linha de comando dos runs do MLflow — sem subir a UI.

Útil na gravação/demo: mostra os experimentos rastreados em `mlruns/` como uma
tabela legível, sem depender do servidor web (que leva ~15-40 s para subir) nem
de one-liners com aspas aninhadas que quebram no PowerShell.

Uso (PowerShell, na raiz do projeto):

    python scripts\\mlflow_report.py                    # todos os runs
    python scripts\\mlflow_report.py --policy linucb    # só uma política
    python scripts\\mlflow_report.py --top 3            # os 3 melhores por reward
    python scripts\\mlflow_report.py --run-id <id>      # detalhe de um run
    python scripts\\mlflow_report.py --compare          # melhor run de cada política
"""

from __future__ import annotations

import argparse
import os
import sys

# MLflow 3.x exige o opt-in explícito para o file store local (mesmo motivo do
# `tracking.py` do pacote): sem isso, `search_runs` levanta exceção.
os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

EXPERIMENT = "adaptive-offers"
TRACKING_URI = "file:./mlruns"

COLUMNS = [
    ("tags.mlflow.runName", "run", 18),
    ("params.policy", "política", 14),
    ("params.horizon", "horizon", 8),
    ("metrics.cumulative_reward", "reward", 12),
    ("metrics.regret_ratio", "regret", 8),
    ("metrics.conversion_rate", "conversão", 10),
    ("metrics.exploration_rate", "exploração", 11),
]


def _load(policy: str | None):
    import mlflow

    mlflow.set_tracking_uri(TRACKING_URI)
    filter_string = f"params.policy = '{policy}'" if policy else ""
    df = mlflow.search_runs(
        experiment_names=[EXPERIMENT],
        filter_string=filter_string,
        order_by=["metrics.cumulative_reward DESC"],
    )
    if df.empty:
        alvo = f" para a política '{policy}'" if policy else ""
        print(f"Nenhum run encontrado{alvo}. Rode antes: adaptive-offers train-all")
        sys.exit(1)
    return df


def _fmt(value, key: str) -> str:
    if value is None or value != value:  # NaN
        return "—"
    if key.startswith("metrics."):
        num = float(value)
        if "reward" in key:
            return f"{num:,.0f}".replace(",", ".")
        return f"{num * 100:.1f}%"
    return str(value)


def _print_table(df) -> None:
    header = "  ".join(f"{label:<{width}}" for _, label, width in COLUMNS)
    print(header)
    print("-" * len(header))
    for _, row in df.iterrows():
        cells = [
            f"{_fmt(row.get(key), key):<{width}}" for key, _, width in COLUMNS
        ]
        print("  ".join(cells))
    print(f"\n{len(df)} run(s) · experimento '{EXPERIMENT}' · store {TRACKING_URI}")


def _print_detail(df, run_id: str) -> None:
    match = df[df["run_id"] == run_id]
    if match.empty:
        print(f"run_id '{run_id}' não encontrado neste experimento.")
        sys.exit(1)
    row = match.iloc[0]
    print(f"run_id      : {row['run_id']}")
    print(f"run_name    : {row.get('tags.mlflow.runName')}")
    print(f"status      : {row.get('status')}")
    print(f"início      : {row.get('start_time')}")
    print("\nparams:")
    for key in sorted(k for k in row.index if k.startswith("params.")):
        print(f"  {key[7:]:<22} {row[key]}")
    print("\nmetrics:")
    for key in sorted(k for k in row.index if k.startswith("metrics.")):
        print(f"  {key[8:]:<22} {row[key]}")


def _print_compare(df) -> None:
    """Melhor run de cada política — a comparação que vai ao pitch."""
    best = df.sort_values("metrics.cumulative_reward", ascending=False)
    best = best.drop_duplicates(subset=["params.policy"], keep="first")
    _print_table(best)
    top = best.iloc[0]
    print(
        f"\nCampeão por reward: {top.get('params.policy')} "
        f"({_fmt(top.get('metrics.cumulative_reward'), 'metrics.cumulative_reward')}) · "
        f"menor regret: {best.loc[best['metrics.regret_ratio'].idxmin(), 'params.policy']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lê os runs do MLflow (file store local) e imprime no terminal.",
    )
    parser.add_argument("--policy", help="filtra por política (baseline, thompson, nilos_ucb, linucb…)")
    parser.add_argument("--top", type=int, metavar="N", help="mostra apenas os N melhores por reward")
    parser.add_argument("--run-id", help="imprime params e métricas de um run específico")
    parser.add_argument("--compare", action="store_true", help="melhor run de cada política")
    args = parser.parse_args()

    df = _load(args.policy)

    if args.run_id:
        _print_detail(df, args.run_id)
    elif args.compare:
        _print_compare(df)
    else:
        _print_table(df.head(args.top) if args.top else df)


if __name__ == "__main__":
    main()
