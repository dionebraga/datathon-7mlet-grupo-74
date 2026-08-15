<div align="center">

# 🔗 Acessos do Projeto

### Todos os links, portas e comandos num só lugar

**Adaptive Offers Platform** · FIAP Pós-Tech `7MLET` · Fase 05 · Datathon · Grupo 74

</div>

---

## ⚡ Subir tudo

```powershell
cd C:\Users\Dione\Desktop\datathon-7mlet-grupo-74\datathon-7mlet-grupo-64
.\.venv\Scripts\Activate.ps1
.\start.ps1
```

Aguarde **até 40 segundos**. Para encerrar: `.\stop.ps1`

> O `start.ps1` abre **uma janela do PowerShell por serviço** — é assim que você
> vê que subiu e mantém o controle. Se seu terminal não mostra nada, os
> processos não são seus: veja [Por que não aparece nada no meu terminal?](#-por-que-não-aparece-nada-no-meu-terminal)

---

## 🌐 As 4 superfícies (local)

| | Superfície | URL | Como subir sozinha |
|:--:|---|---|---|
| 🌐 | **API — landing** | http://localhost:8000 | `adaptive-offers serve` |
| 📘 | **API — Swagger** | http://localhost:8000/docs | idem |
| 📗 | **API — ReDoc** | http://localhost:8000/redoc | idem |
| 🔧 | **API — OpenAPI (JSON)** | http://localhost:8000/openapi.json | idem |
| 📊 | **Dashboard BI** | http://localhost:8503 | `streamlit run dashboard\app.py --server.port 8503` |
| 📈 | **MLflow** | http://localhost:5001 | `mlflow ui --backend-store-uri file:./mlruns --port 5001` |
| 🎨 | **Decision Console** | http://localhost:3000 | `cd frontend` → `npm run dev` |

> ⚠️ **As portas não são as padrão.** MLflow é **5001** (não 5000) e o dashboard
> é **8503** (não 8501). Abrir a porta errada mostra página em branco ou outro app.

### 📈 No MLflow, clique em `Model training`

A aba **`GenAI`** (que abre por padrão em algumas versões) exige backend SQL e
fica **vazia** com o *file store* — isso é esperado, não é falha. Os runs estão
em **`Model training` → Runs**.

A aba **`Artifacts`** de cada run também fica vazia de propósito: registramos
params, métricas e tags; o modelo serializado vive em `artifacts/policies/`.

---

## 🔌 Endpoints da API (14)

Base: `http://localhost:8000`

| Método | Rota | O que faz |
|---|---|---|
| `GET` | [`/health`](http://localhost:8000/health) | Liveness + readiness |
| `GET` | [`/policy`](http://localhost:8000/policy) | Política ativa: nome, versão, métricas |
| `GET` | [`/policy/versions`](http://localhost:8000/policy/versions) | Versões disponíveis |
| `PUT` | `/policy/active` | Troca a política ativa (promoção / rollback) |
| `GET` | [`/offers`](http://localhost:8000/offers) | Catálogo das 6 ofertas |
| `GET` | `/offers/{offer_id}` | Detalhe de uma oferta |
| `POST` | `/decide` | **Decisão auditável** + reason codes |
| `POST` | `/assistant/explain` | Explicação LLM + RAG da decisão |
| `GET` | [`/metrics`](http://localhost:8000/metrics) | Matriz de comparação de políticas |
| `GET` | [`/metrics/regret-curve`](http://localhost:8000/metrics/regret-curve) | Curvas de regret acumulado |
| `GET` | [`/audit`](http://localhost:8000/audit) | Log auditável de decisões |
| `DELETE` | `/audit` | Limpa o log de auditoria |
| `POST` | `/simulate` | Simulação sob demanda |

**Teste rápido** (com a API no ar):

```powershell
$body = @{ age = 66; contact = "cellular"; poutcome = "success"; euribor3m = 0.8 } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/decide -Method Post -Body $body -ContentType "application/json"
```

---

## 📦 Repositório e entregáveis

| | Onde |
|---|---|
| 🐙 **GitHub** | https://github.com/dionebraga/datathon-7mlet-grupo-74 |
| ⚙️ **CI (GitHub Actions)** | https://github.com/dionebraga/datathon-7mlet-grupo-74/actions |
| 🎯 **Pitch (PPTX)** | [`docs/Adaptive-Offers-Pitch-Grupo74.pptx`](docs/Adaptive-Offers-Pitch-Grupo74.pptx) — 25 slides |
| 📄 **Pitch (PDF)** | [`docs/Adaptive-Offers-Pitch-Grupo74.pdf`](docs/Adaptive-Offers-Pitch-Grupo74.pdf) — 25 páginas |
| 📑 **Relatório técnico** | [`reports/technical-report.md`](reports/technical-report.md) |
| 📓 **Notebook de EDA** | [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb) |

---

## 📚 Documentação

| Documento | Conteúdo |
|---|---|
| [`README.md`](README.md) | Visão geral, resultados, mapa do projeto |
| [`COMECE-AQUI.md`](COMECE-AQUI.md) | Do zero às 4 telas + troubleshooting |
| [`docs/mlflow-guia.md`](docs/mlflow-guia.md) | 6 formas de acessar o MLflow |
| [`docs/architecture-azure.md`](docs/architecture-azure.md) | Arquitetura-alvo Azure + FinOps |
| [`docs/mlops-lifecycle.md`](docs/mlops-lifecycle.md) | Ciclo MLOps, approval gate, rollback |
| [`docs/model-card.md`](docs/model-card.md) | Métricas, fairness, limitações |
| [`docs/system-card.md`](docs/system-card.md) | Riscos e guardrails |
| [`docs/lgpd-plan.md`](docs/lgpd-plan.md) | Plano LGPD |
| [`docs/feature-store.md`](docs/feature-store.md) | Feature store offline/online |
| [`reports/offline-evaluation.md`](reports/offline-evaluation.md) | Golden set, DR-OPE, fairness |
| [`reports/algorithmic-strategy.md`](reports/algorithmic-strategy.md) | Estratégia algorítmica |
| [`reports/data-generation.md`](reports/data-generation.md) | Geração dos dados sintéticos |
| [`reports/eda-quality-report.md`](reports/eda-quality-report.md) | EDA e qualidade da base |
| [`data/kaggle/README.md`](data/kaggle/README.md) | Fonte, licença e download da base |

---

## 🧪 Comandos principais

```powershell
# pipeline completo (dados → enriquecimento → treino → avaliação)
adaptive-offers pipeline

# treinar as 5 políticas (1 run cada no MLflow)
adaptive-offers train-all --horizon 6000

# avaliação: golden set + métricas + fairness
adaptive-offers evaluate --horizon 6000 --seed 123

# off-policy Doubly Robust + gate de promoção
adaptive-offers ope --policy linucb --incumbent baseline

# uma decisão auditável
adaptive-offers decide --context examples\context_sample.json

# runs do MLflow no terminal (instantâneo, sem subir a UI)
python scripts\mlflow_report.py --compare

# qualidade
pytest                    # 95 testes
ruff check src tests      # lint
```

---

## 🩺 Verificação rápida

```powershell
# as 4 portas de uma vez
foreach ($p in 8000,8503,5001,3000) {
  try { $c = (Invoke-WebRequest "http://localhost:$p" -TimeoutSec 5 -UseBasicParsing).StatusCode }
  catch { $c = "FECHADA" }
  "  :$p  ->  $c"
}

# ambiente consistente? (roda após mover/renomear a pasta)
python scripts\fix_venv_paths.py
```

---

## 🖥️ Por que não aparece nada no meu terminal?

Se as portas respondem mas o seu terminal está vazio, os processos foram
iniciados por **outra sessão** — outra janela que você fechou, um `.bat`, ou uma
ferramenta externa. Eles continuam de pé porque ninguém os encerrou, mas você
não os controla: não vê o log, não dá `Ctrl+C`, e eles podem cair sozinhos.

**Antes de gravar, assuma o controle dos processos:**

```powershell
.\stop.ps1     # derruba tudo que estiver nas portas do projeto
.\start.ps1    # sobe de novo, agora nas SUAS janelas
```

Para descobrir quem segura uma porta:

```powershell
Get-NetTCPConnection -LocalPort 5001 -State Listen |
  ForEach-Object { Get-Process -Id $_.OwningProcess | Select-Object Id, ProcessName, StartTime }
```

> 💡 Isso também explica o caso clássico de "editei o código e nada mudou": o
> processo antigo continua servindo a versão velha. `.\stop.ps1` resolve.

---

## 📌 Números do projeto

| | |
|---|---|
| Base | Bank Marketing (UCI) · **41.188** contatos reais |
| Políticas | Baseline · Thompson · Nilos-UCB · LinUCB · Neural |
| Melhor valor (seed 123) | Thompson **114.290** (+9,2%) |
| Recomendada | **LinUCB** — regret 8,3% · conversão 9,1% · CV 2,97% |
| DR-OPE | **19,18** · IC95 [17,66 · 20,65] > baseline 16,44 |
| Golden set | **83,3%** (adversarial 5/5 · segmento 6/6) |
| Fairness | exposição **0,00** · flag `review` (grupo de 1 cliente) |
| Testes | **95** passando · ruff limpo |

---

<div align="center">

**Adaptive Offers Platform** · © 2026 **Dione Braga** — Grupo 74 · FIAP Pós-Tech 7MLET · [MIT](LICENSE)

</div>
