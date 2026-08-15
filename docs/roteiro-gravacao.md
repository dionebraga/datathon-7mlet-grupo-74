<div align="center">

# 🎬 Roteiro de Gravação — Adaptive Offers Platform

**FIAP Pós-Tech `7MLET` · Fase 05 · Datathon · Grupo 74 · Dione Braga**

Pitch de **10 minutos** + **5 minutos** de Q&A.

</div>

---

## 📋 Índice

| | |
|---|---|
| [A. Pré-voo (T-15 min)](#a-pré-voo--faça-isso-15-minutos-antes-de-gravar) | [D. Encerramento](#d-encerramento--3040-s) |
| [B. Ordem das janelas](#b-ordem-das-janelas-na-tela) | [E. Banco de respostas (Q&A)](#e-banco-de-respostas--qa) |
| [C. Roteiro minuto a minuto](#c-roteiro-minuto-a-minuto-10-min) | [F. Se algo der errado ao vivo](#f-se-algo-der-errado-ao-vivo) |

---

## A. Pré-voo — faça isso 15 minutos antes de gravar

> ⏱️ Leva ~5 min. **Não pule**: cada item aqui corresponde a uma falha que já
> aconteceu neste projeto.

### A.1 — Checklist de ambiente

```powershell
# 1. Pasta certa (o repo fica DENTRO da pasta de mesmo nome)
cd C:\Users\Dione\Desktop\datathon-7mlet-grupo-74\datathon-7mlet-grupo-64
.\.venv\Scripts\Activate.ps1

# 2. O .venv está consistente com esta pasta? (quebra ao renomear/mover o projeto)
python scripts\fix_venv_paths.py     # esperado: "Nada a corrigir"
#  ↳ se acusar problema:  python scripts\fix_venv_paths.py --apply
python -c "import adaptive_offers; print('OK')"
streamlit --version                  # se der "Fatal error in launcher", rode o --apply acima
mlflow --version

# 3. Testes e lint verdes (é o que o badge do README promete)
pytest -q          # esperado: 93 passed
ruff check src tests   # esperado: All checks passed!

# 4. Modelo ativo alinhado com o deck (6.000 rounds)
adaptive-offers train-all --horizon 6000     # ~50 s
adaptive-offers evaluate --horizon 6000 --seed 123   # ~22 s
```

Os números que devem sair do `train-all` — **são exatamente os do slide 09 e do
README**:

| Política | Reward | Regret | Conversão | Lift |
|---|---:|---:|---:|---:|
| thompson | 114.290 | 11,8% | 7,1% | +9,2% |
| linucb | 113.230 | 8,3% | 9,1% | +8,2% |
| baseline | 104.700 | 10,9% | 6,2% | — |
| nilos_ucb | 102.020 | 17,0% | 7,0% | −2,6% |

> Se os números **não** baterem, pare e investigue antes de gravar — o deck e a
> tela vão se contradizer na frente da banca.

### A.2 — Subir a stack

```powershell
.\start.ps1      # abre 3 janelas: API (8000), MLflow (5001), Dashboard (8503)
```

Aguarde **até 40 s** e confirme cada endereço no navegador:

| Superfície | URL | Sinal de que está pronto |
|---|---|---|
| 🌐 API + Swagger | http://localhost:8000/docs | lista de endpoints renderizada |
| 📊 Dashboard BI | http://localhost:8503 | KPIs preenchidos, sem *spinner* |
| 📈 MLflow | http://localhost:5001 | aba **`Model training`** → 19+ runs |
| 🎨 Decision Console *(opcional)* | http://localhost:3000 | `cd frontend; npm run dev` |

> ⚠️ **Portas**: MLflow é **5001** (não 5000) e o dashboard é **8503** (não 8501).
> Abrir a porta errada mostra página em branco ou outro app.

### A.3 — Higiene de tela

- [ ] Fechar Slack/Teams/e-mail e **silenciar notificações** (Windows: Foco assistido).
- [ ] Zoom do navegador em **110–125%** (a banca lê melhor no vídeo).
- [ ] Abrir as 4 abas **na ordem** da seção B e deixá-las carregadas.
- [ ] Terminal com fonte grande (≥ 16pt) e tema escuro.
- [ ] Deixar o PDF do pitch aberto: `docs/Adaptive-Offers-Pitch-Grupo74.pdf`.
- [ ] Rodar `adaptive-offers decide --context examples\context_sample.json` **uma vez**
      antes de gravar, para o feed de decisões do dashboard não aparecer vazio.

---

## B. Ordem das janelas na tela

Deixe tudo aberto **antes** de começar e apenas alterne (`Alt+Tab` / `Ctrl+Tab`).
Trocar de janela é mais rápido e mais seguro do que abrir na hora.

```
1. PDF do pitch            → narrativa (slides 01 a 09)
2. Dashboard  :8503        → a demo principal
3. Swagger    :8000/docs   → o contrato da API
4. MLflow     :5001        → rastreabilidade
5. Terminal                → decisão via CLI + testes
```

---

## C. Roteiro minuto a minuto (10 min)

### ⏱️ 0:00 – 1:00 · Abertura e problema *(slides 01–02)*

> "Adaptive Offers Platform, Datathon 7MLET, Grupo 74. O problema: uma
> instituição financeira digital precisa decidir, a cada impressão, **qual oferta
> mostrar para aquele cliente, agora**. Hoje isso é resolvido de dois jeitos
> ruins: **regra fixa**, que envelhece e não aprende; ou **teste A/B**, que queima
> semanas de tráfego na variante ruim até dar significância. E os dois otimizam
> conversão — **conversão não é lucro**. Converter mais no produto de margem baixa
> significa ganhar menos."

**Ponto-chave:** deixe claro que a métrica é **valor = P(conversão) × margem**.

### ⏱️ 1:00 – 2:00 · A abordagem *(slides 03–05)*

> "Modelamos como **multi-armed bandit contextual**. Cada braço é uma oferta; o
> contexto é o estado anonimizado do cliente; a recompensa é a conversão
> ponderada pela margem — e ela frequentemente chega **atrasada**. Implementamos
> quatro políticas sob o mesmo contrato: **baseline guloso** como controle,
> **Thompson Sampling**, **Nilos-UCB** (UCB-V, consciente de variância) e
> **LinUCB**, contextual. Mais uma quinta neural em PyTorch."

### ⏱️ 2:00 – 3:00 · Dados, sem maquiagem *(slide 04)*

> "A base é a **Bank Marketing do Kaggle/UCI — 41.188 contatos reais**. Removemos
> a coluna `duration`, que só é conhecida depois do contato: seria **vazamento**.
> Sobre a base real construímos uma **camada sintética** de ofertas, eventos e
> recompensas atrasadas — e é isso que nos permite medir **regret**, porque
> conhecemos o ótimo do gerador. **Nenhum dado pessoal real é usado.**"

### ⏱️ 3:00 – 4:30 · 🖥️ DEMO 1 — Dashboard *(:8503)*

Percorra **nesta ordem**, sem pressa:

1. **⚡ Métricas em tempo real** — 4 KPI tiles com *sparklines*.
   > "Reward por mil, regret ratio, conversão e lift — atualizando a cada 30 s."
2. **📊 Resultados do experimento** — comparação entre políticas.
   > "Aqui está o ranking: Thompson à frente por pouco nesta seed, LinUCB com o
   > **menor regret e a maior conversão**."
3. **🔬 DR-OPE** — avaliação off-policy.
   > "Este painel é o diferencial: reavaliamos as políticas **só com os eventos já
   > logados**, sem expor cliente nenhum."
4. **🧠 Dinâmica de aprendizado** — curva de regret achatando.
   > "A curva achatar significa que a política **aprendeu**."
5. **📡 Feed de decisões ao vivo** — verde = explotação, ciano = exploração.

### ⏱️ 4:30 – 5:30 · 🖥️ DEMO 2 — API e uma decisão real *(:8000/docs + terminal)*

No **Swagger**, abra `POST /decide` → **Try it out** com:

```json
{ "age": 66, "contact": "cellular", "poutcome": "success", "euribor3m": 0.8 }
```

> "A resposta traz o braço escolhido, o **valor esperado**, os **reason codes** e
> a **versão da política**. Isso é o que torna a decisão **auditável**: dá para
> reconstruir, meses depois, por que aquele cliente viu aquela oferta."

No **terminal**, o mesmo pela CLI:

```powershell
adaptive-offers decide --context examples\context_sample.json
```

> ⏱️ **O assistente LLM demora ~20 a 25 segundos** (chamada real ao Claude). Não
> fique em silêncio esperando: dispare o `POST /assistant/explain` e **narre por
> cima** enquanto ele responde — explique que o LLM está **fora do caminho
> crítico** (ele explica a decisão já tomada, não decide nada) e que a mensagem
> ao cliente vem de template governado. Quando a resposta aparecer, leia o
> parecer. Se preferir zero risco, deixe **uma resposta já gerada** numa aba
> aberta e mostre essa.

> **Exemplo que vale narrar** *(slide 07)*: cliente de 60 anos com empréstimo
> ativo → escolhido **Fundo de Investimento**. O **Seguro tinha conversão maior
> (10,9%)**, mas margem de R$ 90 perdeu para o Fundo (8,6% × R$ 180). **A margem
> venceu a conversão** — e o Empréstimo foi cortado pela elegibilidade.

### ⏱️ 5:30 – 6:15 · 🖥️ DEMO 3 — MLflow *(:5001)* + **slides 21–22**

> "Todo treino vira um run rastreado. Aqui estão os 19 runs, com params e
> métricas, e dá para **comparar** políticas lado a lado."

Aba **`Model training`** → selecione 2 runs → **Compare**.

Se a UI estiver lenta, use a alternativa instantânea no terminal (**sem risco**):

```powershell
python scripts\mlflow_report.py --compare
```

**Depois passe aos slides 21 e 22** — é onde a análise dos experimentos está
consolidada, e o slide 21 carrega o melhor argumento do pitch:

> "Olhem este gráfico. O **Baseline tem a MAIOR conversão de todas — 10,6%** — e
> é o que **menos fatura**: R$ 76.560. O LinUCB converte **menos**, 8,6%, e
> entrega **+41% de valor**. Isso é a prova, no nosso próprio experimento, do que
> eu disse no começo: **conversão não é lucro**. O baseline empurra todo mundo
> para a oferta mais fácil de vender; o LinUCB escolhe a oferta certa para o
> perfil certo. É por isso que a recompensa é ponderada por margem."

No **slide 22**, o ponto de robustez:

> "Aqui à direita: **trocando só a seed**, o baseline varia **37%**. Uma seed não
> decide nada — por isso a conclusão do relatório usa cinco."

### ⏱️ 6:15 – 7:15 · Evidências *(slide 09)* — **o momento da honestidade**

> "Na base real o ganho é **modesto: entre 8 e 9%**. Não é o número mágico de
> +60% que a base fac-símile produzia — e eu **troquei aquele número** quando os
> dados reais entraram. Numa seed isolada o Thompson lidera; **em 5 seeds o
> LinUCB é a política recomendada**: maior reward médio, menor regret e o **mais
> estável, com CV de 2,97%** contra 20% do baseline. E **nem todo bandit vence**:
> o Nilos-UCB ficou **abaixo** do baseline, −2,6%. Está no relatório."

> 💡 Esse trecho vale mais que qualquer número inflado. Bancas premiam quem mostra
> resultado negativo junto com o positivo.

### ⏱️ 7:15 – 8:15 · Arquitetura e MLOps *(slides 12–13)*

> "Arquitetura-alvo **100% Azure**: Container Apps para a API, ADLS + Redis para a
> feature store, Azure OpenAI + AI Search para o RAG, Azure ML + MLflow para
> tracking, e **Key Vault + Managed Identity** — sem segredo em variável de
> ambiente. O ciclo MLOps fecha em: feature store → treino rastreado → serving →
> monitor de drift com PSI e KS. **93 testes**, ruff limpo, CI/CD com approval
> gate e **rollback em um comando**."

### ⏱️ 8:15 – 9:15 · Governança e o gate A/B-free *(slides 08 e 14)*

> "O bandit decide **qual oferta**. Quatro camadas determinísticas fecham o
> problema: **segmentação** em 6 personas, **orquestração multi-canal** com
> frequency cap e horário de silêncio, **Next-Best-Action** com mensagem por
> template governado — **nunca texto livre do LLM** — e **IA responsável**."
>
> "E o critério de promoção é **A/B-free**: o **Doubly Robust** com intervalo de
> confiança. Só promovemos se o **limite inferior do IC95** da candidata superar
> o valor da incumbente. LinUCB: 17,66 contra 16,44 do baseline → **aprovado**."

**Se sobrar tempo, seja transparente sobre os dois pontos abertos:**

> "Dois números eu deixo à mostra: o **golden set está em 83,3%**, abaixo do gate
> de 0,95 — adversariais e segmento seguem em 100%, mas casos típicos exigem
> ajuste. E o **flag de fairness sai como `review`**, por conta de um grupo de
> escolaridade com **um único cliente** na amostra. Nenhum dos dois foi
> mascarado."

### ⏱️ 9:15 – 10:00 · Impacto e fechamento *(slide 23)*

> "Uma plataforma que **decide, aprende e se explica**: escolhe em tempo real a
> oferta de maior valor esperado, com governança pronta para produção e **100%
> das decisões auditáveis**. Ganho real e honesto de ~8 a 9% sobre a regra fixa,
> com o menor regret do conjunto. Obrigado."

---

## D. Encerramento — 30/40 s

- [ ] Última frase dita **olhando para a câmera**, não para a tela.
- [ ] Deixar o slide 23 (**"Obrigado"**) visível por ~3 s antes de cortar.
- [ ] Conferir o áudio dos primeiros 30 s antes de exportar.

---

## E. Banco de respostas — Q&A

> Perguntas em ordem de probabilidade. Respostas curtas: 30–45 s cada.

**1. "Por que bandit em vez de A/B?"**
> A/B congela o tráfego numa variante ruim até atingir significância. O bandit
> realoca **continuamente** para o que está funcionando, mantendo um piso de
> exploração. Aqui o baseline apostou 85% no empréstimo; o LinUCB diversificou
> pelo contexto e chegou a menor regret com maior conversão.

**2. "O ganho de 8% não é pouco?"**
> É pouco **e é real**. O fac-símile dava +60% e eu troquei esse número quando a
> base real entrou. Sobre volume de campanha, 8% de valor é material; e o
> argumento mais forte não é o lift, é a **estabilidade**: CV de 2,97% contra 20%
> do baseline. Vale olhar o slide 21: em outra seed o ganho chega a **+41%**,
> justamente porque o baseline é instável — a média de 5 seeds é a leitura honesta.

**2b. "Mas o baseline converte mais. Ele não é melhor?"** *(slide 21)*
> Converte — e é exatamente aí que está o ponto. **10,6% de conversão e o menor
> faturamento de todos.** Ele empurra o cliente para a oferta mais fácil de
> vender, não para a de maior valor esperado. Se a métrica fosse conversão, ele
> ganharia; como a métrica é **margem × conversão**, ele perde por 41%. Foi por
> isso que escolhemos otimizar valor, não cliques.

**3. "Como você sabe que a nova política é melhor sem rodar A/B?"**
> Doubly Robust off-policy: combino um modelo de recompensa com correção por
> propensity e calculo IC por bootstrap. Só promovo se o **limite inferior do IC**
> da candidata bater o valor pontual da incumbente. É conservador de propósito —
> sob baixa sobreposição, ele não promove.

**4. "Os dados são reais ou sintéticos?"**
> A **base é real**: Bank Marketing do UCI, 41.188 contatos. A **camada de
> ofertas e recompensas é sintética**, e isso é deliberado: preciso de um
> **oráculo conhecido** para medir regret, e de recompensa atrasada, que a base
> original não tem. Por isso não afirmo lift financeiro de produção.

**5. "Por que o golden set está em 83% e não passa no gate?"**
> Porque eu não mexi no gate para caber no resultado. Adversariais (5/5) e
> segmento (6/6) estão em 100% — os guardrails críticos funcionam. Os casos
> típicos caem em contextos reais mais heterogêneos. Está documentado como
> limitação assumida no relatório técnico.

**6. "O relatório de fairness diz `review`. Isso é discriminação?"**
> Não, e a evidência é a **exposição: disparidade 0,00** — ninguém deixa de
> receber oferta. O flag vem da disparidade de **valor** em escolaridade (0,32),
> puxada pelo grupo `illiterate`, que tem **1 cliente** nas 6.000 linhas
> avaliadas. É artefato de amostra pequena. Mantive o flag ligado de propósito:
> a correção certa é **agregar grupos com n < 30**, não afrouxar o limiar.

**7. "Onde entra o LLM? Ele decide algo?"**
> **Não.** O LLM está fora do caminho crítico. Ele **explica** a decisão já
> tomada, com RAG sobre as políticas comerciais. A mensagem ao cliente vem de
> **template governado**, nunca de texto livre — para manter suitability
> auditável. Sem chave de API, cai num sumarizador determinístico.

**8. "Como funciona o rollback?"**
> O registry guarda cada versão com hash de conteúdo em
> `artifacts/policies/<versão>/`. Trocar o ponteiro ativo é um comando, e a API
> recarrega o modelo em memória. Se o monitor de reward acusar queda sustentada
> (z < −3), a recomendação é rollback automático.

**9. "Recompensa atrasada quebra o bandit?"**
> Ela atrasa o aprendizado. Modelamos com fila de feedback pendente: a política só
> aprende com recompensas **maturadas**, ~40% delas em 1 a 30 dias. É o motivo de
> o cold-start ter regret maior.

**10. "Por que só uma base do Kaggle?"**
> O edital pede **uma** base compatível. As outras três sugeridas são reuploads ou
> variantes do mesmo problema UCI — não trariam sinal novo. A justificativa está
> em `data/kaggle/README.md`.

**11. "Isso está pronto para produção?"**
> Não, e o system card diz isso explicitamente. É protótipo acadêmico: camada de
> recompensa sintética, sem prontidão regulatória, e decisões sensíveis exigem
> humano no loop.

---

## F. Se algo der errado ao vivo

| Problema | O que fazer **sem parar a gravação** |
|---|---|
| MLflow não abre / lento | `python scripts\mlflow_report.py --compare` no terminal |
| Dashboard travado | recarregue com `Ctrl+F5`; se persistir, mostre a API + terminal |
| API não responde | `adaptive-offers serve` numa janela nova; enquanto sobe, narre o slide 21 |
| Porta ocupada | `.\stop.ps1` e depois `.\start.ps1` |
| `ModuleNotFoundError` ou `Fatal error in launcher` | `python scripts\fix_venv_paths.py --apply` (5 s) |
| Esqueceu um número | está tudo no slide 09 e no README §9 — pode olhar, é natural |
| Travou na fala | **pause, respire, refaça a frase.** Você corta na edição. |

> 🎯 **Regra de ouro:** se uma tela falhar, **não conserte no ar**. Vá para a
> próxima superfície e volte depois. Você tem 4 superfícies — perder uma não
> compromete o pitch.

---

<div align="center">

[⬅ Voltar ao índice da documentação](README.md) · [🏠 README principal](../README.md) · [🚀 COMECE-AQUI](../COMECE-AQUI.md)

</div>
