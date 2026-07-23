# Roteiro de Gravação da Demo — Adaptive Offers Platform

> **Objetivo:** roteiro versionado para a **demonstração gravada** da plataforma
> em operação (Etapa 8 — *desejável, soma pontos extras*). Indica o **cenário**,
> o **passo a passo** (ação + narração), o **plano de contingência** e o
> **versionamento** da gravação e do dataset de demonstração.

- **Duração-alvo:** ~5 min (encaixa no slot de demonstração do pitch de 10 min).
- **Formato:** captura de tela 1080p + narração; exportar em MP4.
- **Grupo:** 74 · FIAP Pós-Tech 7MLET.

---

## 1. Cenário da demonstração

Mostramos o **loop de decisão ponta a ponta** para um cliente **sênior com
conversão prévia bem-sucedida** — o caso que melhor evidencia a personalização
contextual e as 4 camadas fintech (persona → canal → mensagem → próximo passo).

- **Base:** UCI Bank Marketing real (`provenance=real`, 41.188 contatos).
- **Seed fixa da demo:** `123` · **Horizonte:** `2000` (determinístico e
  reproduzível — a mesma seed gera exatamente os mesmos números).
- **Política ativa:** LinUCB (contextual), registrada como ativa.

---

## 2. Setup pré-gravação (fazer ANTES de gravar)

```powershell
# 0) Ambiente
.\.venv\Scripts\Activate.ps1

# 1) Garantir dados reais + política treinada (uma vez)
adaptive-offers pipeline            # dados → synth → treino → avaliação

# 2) Subir os serviços em janelas separadas e DEIXAR RODANDO:
adaptive-offers serve                                   # API  → :8000
streamlit run dashboard\app.py --server.port 8503       # BI   → :8503
$env:MLFLOW_ALLOW_FILE_STORE='true'; mlflow ui --backend-store-uri file:./mlruns --port 5001
```

**Checklist antes de apertar REC:**
- [ ] Dashboard já **carregou** (esperar o "Rodando a simulação real…" sumir — só na 1ª carga).
- [ ] MLflow aberto na aba **`Model training`** (não a `GenAI`), na porta **5001**.
- [ ] Badge do assistente em **offline/"análise ML"** (narrativa Azure-only; não exibir "Claude").
- [ ] Zoom do navegador em 100% e janela limpa (sem abas/notificações).

---

## 3. Roteiro por blocos (ação + narração)

### Bloco 0 · Abertura — `00:00–00:20`
- **Ação:** tela do dashboard aberta, com o fundo "caracol" (fórmulas do bandit no tubo).
- **Narração:** *"Esta é a Adaptive Offers Platform: ela decide, em tempo real e por
  canal, qual oferta, mensagem e próximo passo apresentar a cada cliente elegível —
  aprendendo com multi-armed bandits em vez de regras fixas."*

### Bloco 1 · Experimento e comparação — `00:20–01:20`
- **Ação:** deixar a seed em `123`, clicar **"Simular (2.000 rounds)"**. Mostrar os
  painéis: **Valor acumulado**, **Regret** (área de convergência ao oráculo),
  **Exploração → explotação** e **Conversão por política**.
- **Narração:** *"Comparamos 5 políticas no mesmo cenário. O LinUCB captura mais
  valor e tem o menor regret — e note: **nem todo bandit vence**; o Nilos-UCB fica
  abaixo do baseline. É um resultado honesto, sobre a base real da UCI."*

### Bloco 2 · Explorador de decisão + as 4 camadas — `01:20–03:00`
- **Ação:** ir ao **🧪 Explorador de decisão**. Definir: idade **67**, canal
  **telephone**, resultado anterior **success**, horário **23** (se disponível).
  Clicar **"Decidir oferta"**.
- **Mostrar, no card de resultado:**
  1. **Oferta escolhida** + valor esperado (P×margem) + modo (explotação/exploração).
  2. **Persona** (segmento comportamental) · **Canal de entrega** · **Próximo passo (NBA)**.
  3. **Prévia da mensagem ao cliente** (template governado) — *frisar que é o
     criativo que o cliente receberia, não um botão do painel*.
  4. **Grupo protegido** (auditoria — *não usado para decidir*).
- **Narração:** *"O bandit escolhe a oferta; quatro camadas fecham o problema: a
  persona, o canal — aqui o horário de silêncio derrubou a ligação e caiu no
  e-mail — a mensagem por template governado, e o próximo passo. Tudo auditável."*

### Bloco 3 · Assistente LLM + RAG — `03:00–03:50`
- **Ação:** rolar até **🧠 Raciocínio da decisão & Assistente LLM + RAG**. Mostrar
  as seções (Decisão, Justificativa técnica, Por que venceu, Risco & governança,
  **Orquestração & próximo passo**, Leitura comercial) e as **citações de política**
  (chunks recuperados por RAG com score). Abrir o expander **"Rastreio de execução"**.
- **Narração:** *"O assistente explica a decisão em linguagem natural, ancorado nos
  números reais e nas políticas comerciais recuperadas por RAG — sem inventar dados."*

### Bloco 4 · Serviço auditável (API) — `03:50–04:30`
- **Ação:** abrir **http://localhost:8000/docs**, executar `POST /decide` com um
  contexto de exemplo. Mostrar a resposta: braço, `reason_codes`, versão da política,
  canal, NBA e `protected_groups`. No terminal, mostrar a última linha de
  `artifacts\decisions\audit.jsonl` (log auditável).
- **Narração:** *"A mesma decisão via API, com contrato documentado e log auditável —
  reason codes, versão da política e registro de cada decisão."*

### Bloco 5 · MLOps / MLflow — `04:30–05:00`
- **Ação:** MLflow na aba **`Model training`** → experimento `adaptive-offers` →
  selecionar os runs do `train-all` → **Compare**.
- **Narração:** *"Todo experimento é rastreado no MLflow. Uma nova política sai de
  experimento para produção por approval gate, canary e rollback — documentado no
  ciclo MLOps. A arquitetura-alvo é 100% Azure."*

---

## 4. Plano de contingência

| Risco na hora | Contingência |
|---|---|
| Demo ao vivo falha / trava | Usar a **gravação versionada** (este roteiro reproduz o vídeo em `docs/demo/`) |
| Dashboard demora a carregar | Já deixar carregado antes de gravar; a 1ª carga treina e cacheia |
| Porta 5001/8000/8503 ocupada | Trocar a porta no comando; conferir com `netstat -ano \| findstr <porta>` |
| Sem internet / LLM online indisponível | Assistente roda **offline ("análise ML")** — decisão independe do LLM |
| Números diferentes | Fixar **seed 123 / horizonte 2000** — determinístico |

---

## 5. Versionamento da gravação e do dataset de demonstração

- **Gravação:** salvar o MP4 em `docs/demo/adaptive-offers-demo.mp4` e versionar
  (ou, se pesar demais para o Git, subir em release/Drive e **linká-lo aqui** +
  no README). Registrar data e commit correspondente.
- **Dataset de demonstração:** a demo usa a **base real** + **seed 123 / horizonte
  2000** — reprodutível por qualquer avaliador com `adaptive-offers pipeline` e a
  mesma seed. Não há dataset separado a versionar além do já versionado
  (`data/processed/provenance.json`, `data/synthetic_enrichment/schema.json`).
- **Cenário e roteiro:** este arquivo (`docs/demo-roteiro.md`) é a fonte versionada
  do cenário e do plano de contingência.
