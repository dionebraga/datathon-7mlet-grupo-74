"""Gera os gráficos de análise dos experimentos do MLflow (PNG) para o deck e a documentação.

Lê os runs direto do `mlruns/` (nada de screenshot manual: os números vêm sempre da
fonte de verdade) e escreve PNGs em `docs/img/mlflow/`, na paleta escura do deck.

    python scripts\\build_mlflow_charts.py

Gráficos gerados:
  1. mlflow-valor-vs-conversao.png  — a prova de que "conversão não é lucro"
  2. mlflow-metricas.png            — painel 2x2 das métricas-chave por política
  3. mlflow-sensibilidade-seed.png  — por que uma seed só não decide nada

⚠️ Todos os gráficos são do recorte **horizon=6000, seed=42** (os runs do
`train-all`), EXCETO o de sensibilidade. O deck/README usam **seed=123** (os runs
do `evaluate`). Os títulos trazem o seed explícito de propósito — sem isso, os
números pareceriam contradizer o slide 09.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

import mlflow  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "docs" / "img" / "mlflow"
EXPERIMENT = "adaptive-offers"

# Paleta do deck (scripts/update_pptx_colors.py)
BG = "#000000"
PANEL = "#030D24"
TEXT = "#EDEDED"
MUTED = "#8A93A6"
GRID = "#1A2340"

COLORS = {
    "linucb": "#FFC200",        # gold — a política recomendada
    "thompson": "#1A9E1A",      # green
    "nilos_ucb": "#FF9A00",     # amber
    "baseline": "#E84000",      # red — o controle
    "lin_thompson": "#1A6FFF",  # cyan
}
LABELS = {
    "linucb": "LinUCB",
    "thompson": "Thompson",
    "nilos_ucb": "Nilos-UCB",
    "baseline": "Baseline",
    "lin_thompson": "LinThompson",
}

BASE_LAYOUT = dict(
    paper_bgcolor=BG,
    plot_bgcolor=PANEL,
    font=dict(family="Segoe UI, Arial", color=TEXT, size=15),
    margin=dict(l=70, r=40, t=90, b=60),
    showlegend=False,
)
AXIS = dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, tickfont=dict(color=MUTED))


def load_runs():
    mlflow.set_tracking_uri(f"file:{(PROJECT_ROOT / 'mlruns').as_posix()}")
    df = mlflow.search_runs(experiment_names=[EXPERIMENT])
    if df.empty:
        raise SystemExit("nenhum run encontrado — rode antes: adaptive-offers train-all --horizon 6000")
    df = df.rename(columns=lambda c: c.replace("metrics.", "m_").replace("params.", "p_"))
    return df


def slice_runs(df, horizon: int, seed: int):
    """Runs de um recorte, sem duplicatas (train-all repetido gera runs idênticos)."""
    sub = df[(df["m_rounds"] == horizon) & (df["m_seed"] == seed)]
    sub = sub.drop_duplicates(subset=["p_policy"], keep="first")
    order = ["linucb", "thompson", "nilos_ucb", "baseline", "lin_thompson"]
    sub = sub.set_index("p_policy").reindex([p for p in order if p in set(sub["p_policy"])])
    return sub.reset_index()


def chart_value_vs_conversion(sub, out: Path) -> None:
    """O gráfico que sustenta a tese do pitch: converter mais ≠ faturar mais."""
    fig = go.Figure()
    for _, r in sub.iterrows():
        pol = r["p_policy"]
        fig.add_trace(go.Scatter(
            x=[r["m_conversion_rate"] * 100],
            y=[r["m_cumulative_reward"]],
            mode="markers+text",
            marker=dict(size=26, color=COLORS[pol],
                        line=dict(width=2, color=BG)),
            text=[f"  {LABELS[pol]}"],
            textposition="middle right",
            textfont=dict(color=TEXT, size=15),
        ))

    base = sub[sub["p_policy"] == "baseline"].iloc[0]
    lin = sub[sub["p_policy"] == "linucb"].iloc[0]
    ganho = (lin["m_cumulative_reward"] / base["m_cumulative_reward"] - 1) * 100

    # Seta do Baseline PARA o LinUCB: a direção da melhoria.
    fig.add_annotation(
        x=lin["m_conversion_rate"] * 100, y=lin["m_cumulative_reward"],
        ax=base["m_conversion_rate"] * 100, ay=base["m_cumulative_reward"],
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5, arrowcolor="#FFC200",
        standoff=18, startstandoff=18,
    )
    # Callout no quadrante superior direito, que fica vazio neste recorte.
    fig.add_annotation(
        x=0.97, y=0.97, xref="paper", yref="paper",
        xanchor="right", yanchor="top", showarrow=False, align="right",
        text=(f"<b>Converter mais ≠ faturar mais</b><br>"
              f"Baseline: {base['m_conversion_rate'] * 100:.1f}% de conversão,<br>"
              f"o MAIOR — e o MENOR valor.<br>"
              f"<b style='color:#FFC200'>LinUCB: {ganho:+.0f}% de valor</b> "
              f"com {lin['m_conversion_rate'] * 100:.1f}%."),
        font=dict(color=TEXT, size=16),
        bgcolor="rgba(3,13,36,0.92)", bordercolor="#FFC200", borderwidth=2, borderpad=14,
    )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Valor acumulado × taxa de conversão</b><br>"
                 "<sup>MLflow · 6.000 rounds · seed=42 · Bank Marketing (UCI)</sup>",
            x=0.02, xanchor="left", y=0.94, font=dict(size=21)),
        xaxis=dict(**AXIS, title="taxa de conversão (%)"),
        yaxis=dict(**AXIS, title="reward acumulado (R$)"),
    )
    fig.update_xaxes(range=[6.0, 12.4])
    fig.update_yaxes(range=[72000, 118000])
    fig.write_image(out, width=1150, height=720, scale=2)
    print(f"  {out.name}")


def chart_metrics_panel(sub, out: Path) -> None:
    """Painel 2x2 — as quatro métricas que a banca vai olhar."""
    metrics = [
        ("m_cumulative_reward", "Reward acumulado (R$)", 1.0, ",.0f"),
        ("m_regret_ratio", "Regret ratio (%) — menor é melhor", 100.0, ".1f"),
        ("m_conversion_rate", "Conversão (%)", 100.0, ".2f"),
        ("m_exploration_rate", "Exploração (%)", 100.0, ".1f"),
    ]
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[m[1] for m in metrics],
        vertical_spacing=0.20, horizontal_spacing=0.13,
    )

    for i, (col, _, scale, fmt) in enumerate(metrics):
        row, cc = divmod(i, 2)
        vals = (sub[col] * scale).tolist()
        names = [LABELS[p] for p in sub["p_policy"]]
        cols_ = [COLORS[p] for p in sub["p_policy"]]
        fig.add_trace(
            go.Bar(x=names, y=vals, marker_color=cols_,
                   text=[format(v, fmt).replace(",", ".") for v in vals],
                   textposition="outside",
                   textfont=dict(color=TEXT, size=13),
                   cliponaxis=False),
            row=row + 1, col=cc + 1,
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Comparação de políticas — runs do MLflow</b><br>"
                 "<sup>6.000 rounds · seed=42 · 1 run por política</sup>",
            x=0.02, xanchor="left", font=dict(size=21)),
        bargap=0.45,
    )
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    for ann in fig.layout.annotations:
        ann.font.color = TEXT
        ann.font.size = 14
    fig.write_image(out, width=1150, height=780, scale=2)
    print(f"  {out.name}")


def chart_seed_sensitivity(df, out: Path) -> None:
    """Mesmo horizonte, seeds diferentes — por que uma seed só não decide nada.

    seed=42 vem dos runs do MLflow (`train-all`); seed=123 vem do
    `artifacts/evaluation_report.json` (`evaluate`), que é a fonte dos números
    do slide 09 e do README.
    """
    import json

    report_path = PROJECT_ROOT / "artifacts" / "evaluation_report.json"
    if not report_path.exists():
        print("  [pulado] mlflow-sensibilidade-seed.png — rode antes: adaptive-offers evaluate")
        return

    report = json.loads(report_path.read_text(encoding="utf-8"))
    s123 = {m["policy"]: m["cumulative_reward"] for m in report["metrics_matrix"]}
    s42 = slice_runs(df, 6000, 42).set_index("p_policy")["m_cumulative_reward"].to_dict()

    order = ["linucb", "thompson", "nilos_ucb", "baseline"]
    common = [p for p in order if p in s42 and p in s123]
    if not common:
        print("  [pulado] mlflow-sensibilidade-seed.png — sem políticas em comum")
        return

    a = [s42[p] for p in common]
    b = [s123[p] for p in common]
    names = [LABELS[p] for p in common]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=a, name="seed 42  (train-all)", marker_color="#1A6FFF",
        text=[f"{v:,.0f}".replace(",", ".") for v in a],
        textposition="outside", textfont=dict(color=TEXT, size=13), cliponaxis=False))
    fig.add_trace(go.Bar(
        x=names, y=b, name="seed 123  (evaluate — o do deck)", marker_color="#FFC200",
        text=[f"{v:,.0f}".replace(",", ".") for v in b],
        textposition="outside", textfont=dict(color=TEXT, size=13), cliponaxis=False))

    # Destaca o baseline, cuja variação entre seeds é a maior de todas.
    i = common.index("baseline")
    var = (s123["baseline"] / s42["baseline"] - 1) * 100
    fig.add_annotation(
        x=names[i], y=max(s42["baseline"], s123["baseline"]),
        yshift=58, showarrow=False,
        text=f"<b>Baseline varia {var:+.0f}%<br>só trocando a seed</b>",
        font=dict(color="#E84000", size=15),
        bgcolor="rgba(3,13,36,0.92)", bordercolor="#E84000", borderwidth=2, borderpad=8,
    )

    layout = dict(BASE_LAYOUT)
    layout["showlegend"] = True
    layout["margin"] = dict(l=70, r=40, t=110, b=60)
    fig.update_layout(
        **layout,
        barmode="group", bargap=0.35,
        legend=dict(font=dict(color=TEXT, size=13), bgcolor=PANEL,
                    orientation="h", x=0.5, xanchor="center", y=1.08),
        title=dict(
            text="<b>A mesma política, duas seeds</b><br>"
                 "<sup>6.000 rounds · por isso a conclusão do relatório usa 5 seeds, não uma</sup>",
            x=0.02, xanchor="left", y=0.95, font=dict(size=21)),
        xaxis=dict(**AXIS),
        yaxis=dict(**AXIS, title="reward acumulado (R$)", range=[0, 145000]),
    )
    fig.write_image(out, width=1150, height=680, scale=2)
    print(f"  {out.name}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_runs()
    sub = slice_runs(df, 6000, 42)
    if sub.empty:
        raise SystemExit("sem runs em horizon=6000/seed=42 — rode: adaptive-offers train-all --horizon 6000")

    print(f"gerando gráficos em {OUT_DIR.relative_to(PROJECT_ROOT)}:")
    chart_value_vs_conversion(sub, OUT_DIR / "mlflow-valor-vs-conversao.png")
    chart_metrics_panel(sub, OUT_DIR / "mlflow-metricas.png")
    chart_seed_sensitivity(df, OUT_DIR / "mlflow-sensibilidade-seed.png")
    print("\nok — agora rode: python scripts\\add_mlflow_slide.py")


if __name__ == "__main__":
    main()
