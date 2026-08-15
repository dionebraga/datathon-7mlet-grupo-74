<div align="center">

# 🚀 COMECE AQUI

### Tudo o que você precisa para colocar a **Adaptive Offers Platform** no ar

*Do zero até as 4 telas funcionando. Se você só tem 2 minutos, leia a [Rota Rápida](#-rota-rápida--2-minutos).*

**FIAP Pós-Tech `7MLET` · Fase 05 · Datathon · Grupo 74**

</div>

---

## ⚡ Rota Rápida — 2 minutos

Você já rodou o projeto antes e só quer subir tudo:

```powershell
cd C:\Users\Dione\Desktop\datathon-7mlet-grupo-74\datathon-7mlet-grupo-64
.\.venv\Scripts\Activate.ps1
.\start.ps1
```

Aguarde **até 40 segundos** e abra:

| | Superfície | URL |
|:--:|---|---|
| 🌐 | **API + Swagger** | http://localhost:8000/docs |
| 📊 | **Dashboard BI** | http://localhost:8503 |
| 📈 | **MLflow** | http://localhost:5001 → aba **`Model training`** |

Para encerrar tudo: `.\stop.ps1`

> 🎬 Vai **gravar o pitch**? Vá direto para o
> [**roteiro de gravação**](docs/roteiro-gravacao.md) — ele tem o pré-voo completo.

---

## 📍 Antes de tudo: a pasta certa

Este é o detalhe que mais faz perder tempo. O repositório fica **dentro** de uma
pasta de nome parecido:

```
C:\Users\Dione\Desktop\
└── datathon-7mlet-grupo-74\          ← pasta externa (atalhos .bat)
    ├── INICIAR-PROJETO.bat
    ├── VER-API.bat
    ├── VER-DASHBOARD.bat
    ├── VER-MLFLOW.bat
    └── datathon-7mlet-grupo-64\      ← 👈 O REPOSITÓRIO É AQUI
        ├── README.md
        ├── start.ps1
        ├── src\  dashboard\  docs\  tests\
        └── .venv\
```

**Todo comando deste guia roda na pasta interna.** Como confirmar:

```powershell
# você está no lugar certo se este arquivo existir:
Test-Path .\pyproject.toml     # deve retornar True
```

> ⚠️ **Nunca rode `git` a partir de `C:\Users\Dione`** — a pasta home é, por
> acidente, um repositório git de outro projeto. Comandos git ali afetam
> arquivos que não têm nada a ver com este trabalho.

> 💡 **Não gosta de terminal?** Dê **duplo-clique** em `INICIAR-PROJETO.bat` (na
> pasta externa): ele abre um PowerShell já na pasta certa e com o `.venv` ativo.

---

## 🧰 Instalação do zero

Só é necessário na primeira vez ou em uma máquina nova.

### Pré-requisitos

| Item | Versão | Como conferir |
|---|---|---|
| **Python** | 3.11 ou 3.12 | `python --version` |
| **git** | qualquer recente | `git --version` |
| Node.js *(opcional)* | 18+ | `node --version` — só para o Decision Console |
| Docker *(opcional)* | qualquer | `docker --version` |

### Passo a passo

```powershell
# 1) Clonar (ou entrar na pasta que já existe)
git clone https://github.com/dionebraga/datathon-7mlet-grupo-74.git
cd datathon-7mlet-grupo-74

# 2) Criar e ativar o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1
#  ↳ se der erro de política de execução, rode UMA vez:
#    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3) Instalar o pacote + extras de dev e dashboard
pip install -e ".[dev,bi]"

# 4) Configuração (funciona sem editar nada)
Copy-Item .env.example .env

# 5) Confirmar que instalou de verdade
python -c "import adaptive_offers; print('OK')"
adaptive-offers --version
```

### 🔴 Os dois erros nº 1 — ambos causados por **mover ou renomear a pasta**

Um virtualenv grava **caminhos absolutos** em dois lugares. Se a pasta mudar de
nome ou de lugar, os dois apontam para o vazio — e os sintomas são traiçoeiros
porque **`pytest` continua passando** (o `pyproject` injeta `src` no path) e
`python -m <modulo>` também continua funcionando.

**Sintoma A — o pacote some:**

```
ModuleNotFoundError: No module named 'adaptive_offers'
```

**Sintoma B — os comandos somem** (`streamlit`, `mlflow`, `uvicorn`, `pytest`,
até o `pip`):

```
Fatal error in launcher: Unable to create process using
'"C:\...\caminho-antigo\.venv\Scripts\python.exe" "C:\...\caminho-novo\.venv\Scripts\streamlit.exe" ...'
```

> 👀 Repare na mensagem: **dois caminhos diferentes**. O da esquerda é o que
> ficou gravado dentro do `.exe` quando ele foi instalado; o da direita é onde
> ele está hoje. É essa divergência que quebra tudo.

**A solução para os dois — um comando:**

```powershell
python scripts\fix_venv_paths.py           # diagnóstico (não altera nada)
python scripts\fix_venv_paths.py --apply   # corrige
```

Valide depois com:

```powershell
python -c "import adaptive_offers; print('OK')"
streamlit --version
mlflow --version
```

<details>
<summary>Se preferir resolver na mão</summary>

```powershell
# sintoma A apenas
pip install -e . --no-deps

# sintoma B apenas (regenera os launchers do pip)
python -m pip install --force-reinstall --no-deps streamlit mlflow uvicorn pytest pip

# solução definitiva: recriar o ambiente do zero
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,bi]"
```
</details>

---

## ▶️ Rodar o pipeline completo

```powershell
# tudo de uma vez: dados → enriquecimento → treino → avaliação (~30 s)
adaptive-offers pipeline

# uma decisão de exemplo, em JSON
adaptive-offers decide --context examples\context_sample.json
```

### Comandos por etapa

| Comando | Etapa | O que entrega |
|---|:--:|---|
| `adaptive-offers data build` | 1 | Base processada, sem vazamento, com proveniência |
| `adaptive-offers synth generate` | 2 | Catálogo de ofertas, eventos e recompensas atrasadas |
| `adaptive-offers train --horizon 6000 --seed 42` | 3 | Treina **uma** política e registra como ativa |
| `adaptive-offers train-all --horizon 6000` | 3 | Treina **as 5** políticas (1 run cada no MLflow) |
| `adaptive-offers evaluate --horizon 6000 --seed 123` | 4 | Golden set, matriz de métricas e fairness |
| `adaptive-offers ope --policy linucb --incumbent baseline` | 4/7 | Doubly Robust + gate de promoção |
| `adaptive-offers decide` | 5 | Decisão auditável com reason codes |
| `adaptive-offers serve` | 5 | Sobe a API REST |
| `adaptive-offers monitor` | 7 | Relatório HTML de drift e fairness |
| `pytest` | — | 93 testes (unit + integração) |

> 💾 **Sem credenciais do Kaggle?** O carregador usa um **gerador determinístico**
> que reproduz o *schema* da base — todo o pipeline roda offline. Para usar a base
> real (recomendado), veja [`data/kaggle/README.md`](data/kaggle/README.md).

---

## 👀 As 4 superfícies

| | O quê | Como subir | URL |
|:--:|---|---|---|
| 🌐 | **API + Swagger** | `adaptive-offers serve` | http://localhost:8000/docs |
| 📊 | **Dashboard BI** | `streamlit run dashboard\app.py --server.port 8503` | http://localhost:8503 |
| 📈 | **MLflow** | veja o [guia dedicado](docs/mlflow-guia.md) | http://localhost:5001 |
| 🎨 | **Decision Console** | `cd frontend; npm install; npm run dev` | http://localhost:3000 |

Ou tudo junto com **`.\start.ps1`** (abre uma janela por serviço).

> ⚠️ **As portas não são as padrão.** MLflow usa **5001** (a 5000 colide com
> outros serviços no Windows) e o dashboard usa **8503** (não 8501). Todos os
> atalhos `.bat` e o `start.ps1` já usam as corretas.

### Atalhos de duplo-clique (pasta externa)

| Arquivo | O que faz |
|---|---|
| `INICIAR-PROJETO.bat` | Abre o PowerShell na pasta certa, com `.venv` ativo |
| `VER-API.bat` | Mata a API antiga na 8000 e sobe uma nova |
| `VER-DASHBOARD.bat` | Mata qualquer Streamlit travado e sobe na 8503 |
| `VER-MLFLOW.bat` | Mata a UI antiga na 5001 e sobe o MLflow |

### Testar a API pelo PowerShell

```powershell
# decisão para um cliente sênior com sucesso prévio
$body = @{ age = 66; contact = "cellular"; poutcome = "success"; euribor3m = 0.8 } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/decide -Method Post -Body $body -ContentType "application/json"

# explicação da decisão (assistente LLM/RAG)
Invoke-RestMethod -Uri "http://localhost:8000/assistant/explain?question=Por que essa oferta?" `
  -Method Post -Body $body -ContentType "application/json"

# log auditável
Get-Content artifacts\decisions\audit.jsonl -Tail 5
```

---

## 🤖 Ligar o Claude no assistente (opcional)

Sem chave, o assistente usa um **sumarizador determinístico** — funciona, não
alucina, e o badge mostra **⚡ análise ML**. Para ligar o Claude:

```dotenv
# .env, na raiz do projeto
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...     # console.anthropic.com/settings/keys
ANTHROPIC_MODEL=claude-opus-4-8
```

> A chave é lida **só na inicialização**: depois de editar o `.env`, **reinicie**
> a API e o dashboard para o badge virar **● Claude online**.
> O `.env` está no `.gitignore` — **nunca** faça commit da chave.

---

## ✅ Verificar que está tudo saudável

```powershell
pytest -q                 # esperado: 93 passed
ruff check src tests      # esperado: All checks passed!
python -c "import adaptive_offers; print('OK')"
python scripts\mlflow_report.py --compare    # tabela de runs
```

Os números do `train-all --horizon 6000` devem bater com o README §9 e o slide 09:

| Política | Reward | Regret | Conversão | Lift |
|---|---:|---:|---:|---:|
| thompson | 114.290 | 11,8% | 7,1% | +9,2% |
| linucb | 113.230 | 8,3% | 9,1% | +8,2% |
| baseline | 104.700 | 10,9% | 6,2% | — |
| nilos_ucb | 102.020 | 17,0% | 7,0% | −2,6% |

---

## 🩹 Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: adaptive_offers` | `.pth` aponta para pasta antiga | `python scripts\fix_venv_paths.py --apply` |
| `Fatal error in launcher: Unable to create process` | `.exe` do venv aponta para pasta antiga | `python scripts\fix_venv_paths.py --apply` |
| `O sistema não pode encontrar o arquivo especificado` ao rodar `streamlit`/`mlflow` | idem acima **ou** pasta errada | confira `Test-Path .\pyproject.toml` e rode o `fix_venv_paths.py` |
| `Activate.ps1 não pode ser carregado` | política de execução | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| Página em branco na 5001 | MLflow ainda subindo | espere o `Uvicorn running` (até 40 s) |
| MLflow: aba `GenAI` vazia | precisa de backend SQL | use a aba **`Model training`** |
| `MLFLOW_ALLOW_FILE_STORE` exigido | MLflow 3.x + file store | `$env:MLFLOW_ALLOW_FILE_STORE='true'` |
| Dashboard abre versão antiga | Streamlit velho em outra porta | `VER-DASHBOARD.bat` (mata todos e sobe na 8503) |
| `Address already in use` | serviço anterior preso | `.\stop.ps1` e depois `.\start.ps1` |
| Dashboard sem dados | pipeline nunca rodou | `adaptive-offers pipeline` |
| Feed de decisões vazio | nenhuma decisão logada | `adaptive-offers decide --context examples\context_sample.json` |
| `make` não encontrado | Windows não tem `make` | use os comandos `adaptive-offers ...` diretamente |

---

## 📚 Para onde ir agora

| Você quer… | Leia |
|---|---|
| 🎬 **Gravar o pitch** | [`docs/roteiro-gravacao.md`](docs/roteiro-gravacao.md) |
| 📈 Explorar os experimentos | [`docs/mlflow-guia.md`](docs/mlflow-guia.md) |
| 📖 Entender o projeto inteiro | [`README.md`](README.md) |
| 📑 Ler o relatório técnico | [`reports/technical-report.md`](reports/technical-report.md) |
| 🪪 Ver métricas, fairness e limites | [`docs/model-card.md`](docs/model-card.md) |
| ☁️ Ver a arquitetura Azure | [`docs/architecture-azure.md`](docs/architecture-azure.md) |
| 🔁 Entender promoção e rollback | [`docs/mlops-lifecycle.md`](docs/mlops-lifecycle.md) |
| 📂 Ver toda a documentação | [`docs/README.md`](docs/README.md) |

---

<div align="center">

**Adaptive Offers Platform** · © 2026 **Dione Braga** — Grupo 74 · FIAP Pós-Tech 7MLET · [MIT](LICENSE)

</div>
