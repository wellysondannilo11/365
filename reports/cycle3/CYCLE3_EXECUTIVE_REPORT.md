# ROBO DA BET V16+ — CICLO 3 — EXECUTIVE QUANT REPORT

## Estado científico

```text
REAL_MONEY = DISABLED
EDGE = NOT_PROVEN
EXACT_PIT = 0
REAL_ROI = NOT_AVAILABLE
REAL_CLV = NOT_AVAILABLE
REAL_PROFIT_UNITS = NOT_AVAILABLE
```

Todas as análises de preço, seleção e portfolio deste ciclo são `COUNTERFACTUAL_NON_PIT`. O holdout final permaneceu fora da otimização e das simulações.

## 1. Pergunta executiva

> O Robo ficou melhor em seleção, ROI/Units teóricas, ou apenas em previsão?

**Veredito:** a melhora preditiva observada no Ciclo 2 **não se converteu em uma melhora robusta de seleção**. O único sinal positivo de seleção do `ROBO_BASELINE` no primeiro fold desaparece no walk-forward exploratório: 0 de 4 folds positivos para `EV>0`, com retorno agregado negativo. O candidato `ROBO + MARKET` e o `FULL` também não demonstraram seleção superior ao market-only.

## 2. Comparação preditiva — janela OOS compatível com o Ciclo 2

| Configuração | N | LogLoss | Brier | Accuracy | ECE | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|
| MARKET_ONLY | 500 | 0.646162 | 0.228408 | 0.610 | 0.029541 | 0.648129 |
| MARKET | 500 | 0.646787 | 0.228510 | 0.606 | 0.045138 | 0.651162 |
| FULL | 500 | 0.648410 | 0.229062 | 0.608 | 0.035835 | 0.651389 |
| BASELINE | 500 | 0.651768 | 0.230564 | 0.598 | 0.024103 | 0.638950 |

**Leitura:** os números reproduzem a comparação do Ciclo 2 no mesmo primeiro fold: `MARKET_ONLY` 0.646162, `MARKET` 0.646787, `FULL` 0.648410 e `BASELINE` 0.651768. Portanto, o melhor sinal preditivo continua sendo o benchmark de mercado; `ROBO + MARKET` melhora claramente sobre o Robo baseline, mas ainda não supera o market-only.

## 3. Pricing / EV no common sample

| Configuração | N | EV médio | % EV positivo |
|---|---:|---:|---:|
| BASELINE | 500 | 5.03% | 49.60% |
| FULL | 500 | -2.83% | 37.00% |
| MARKET | 500 | -1.60% | 32.20% |
| MARKET_ONLY | 500 | -6.35% | 0.00% |

Atenção: EV positivo aqui é somente estimativa contrafactual baseada em preço não-PIT.

## 4. Seleção no common sample — Home Win

| Configuração | Threshold | N apostas | ROI teórico | Units | Max DD | Profit Factor |
|---|---|---:|---:|---:|---:|---:|
| BASELINE | ALL | 500 | -4.59% | -22.95 | 48.63 | 0.918 |
| BASELINE | EV>0 | 248 | 1.55% | 3.85 | 23.05 | 1.025 |
| BASELINE | EV>5% | 204 | -0.21% | -0.43 | 16.77 | 0.997 |
| BASELINE | EV>10% | 160 | -3.67% | -5.88 | 18.24 | 0.946 |
| FULL | ALL | 500 | -4.59% | -22.95 | 48.63 | 0.918 |
| FULL | EV>0 | 185 | -11.69% | -21.63 | 24.94 | 0.798 |
| FULL | EV>5% | 91 | -17.23% | -15.68 | 19.86 | 0.725 |
| FULL | EV>10% | 50 | -35.86% | -17.93 | 19.23 | 0.488 |
| MARKET | ALL | 500 | -4.59% | -22.95 | 48.63 | 0.918 |
| MARKET | EV>0 | 161 | -5.65% | -9.10 | 24.75 | 0.902 |
| MARKET | EV>5% | 61 | -20.97% | -12.79 | 17.34 | 0.722 |
| MARKET | EV>10% | 27 | -14.81% | -4.00 | 8.55 | 0.810 |
| MARKET_ONLY | ALL | 500 | -4.59% | -22.95 | 48.63 | 0.918 |
| MARKET_ONLY | EV>0 | 0 | N/D | 0.00 | 0.00 | N/D |
| MARKET_ONLY | EV>5% | 0 | N/D | 0.00 | 0.00 | N/D |
| MARKET_ONLY | EV>10% | 0 | N/D | 0.00 | 0.00 | N/D |

### Interpretação

O `ROBO_BASELINE` apresentou `+1,55%` no primeiro fold com `EV>0`, mas isso não é robusto: no walk-forward secundário houve **0/4 folds positivos**. Portanto, esse resultado é classificado como **instabilidade / research-only**, não como edge.

`ROBO + MARKET` e `FULL` foram negativos nos thresholds pesquisados. O `MARKET_ONLY` não produz oportunidades com EV positivo porque o próprio preço observado é usado para construir a probabilidade implícita; isso é esperado sob essa definição e não significa que o mercado seja sempre perdedor.

## 5. EV discrimination

| configuration   | target   | ev_bucket   |   n |   win_rate |     mean_ev |   median_ev |   mean_odds | theoretical_status     |
|:----------------|:---------|:------------|----:|-----------:|------------:|------------:|------------:|:-----------------------|
| BASELINE        | home_win | EV < 0      | 252 |   0.503968 | -0.117266   | -0.102509   |     1.88413 | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | 0–2%        |  20 |   0.5      |  0.00981583 |  0.00928156 |     2.21    | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | 2–5%        |  24 |   0.5      |  0.0345201  |  0.0346878  |     2.21083 | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | 5–10%       |  44 |   0.477273 |  0.0739488  |  0.0752552  |     2.8     | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | 10–15%      |  32 |   0.46875  |  0.126441   |  0.130064   |     2.55406 | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | 15–20%      |  32 |   0.25     |  0.17894    |  0.1809     |     2.98219 | COUNTERFACTUAL_NON_PIT |
| BASELINE        | home_win | >20%        |  96 |   0.291667 |  0.423472   |  0.333546   |     3.94896 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | EV < 0      | 315 |   0.453968 | -0.089697   | -0.0761463  |     2.4073  | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | 0–2%        |  38 |   0.526316 |  0.0097839  |  0.0101029  |     2.26632 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | 2–5%        |  56 |   0.428571 |  0.0332367  |  0.0308807  |     2.30268 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | 5–10%       |  41 |   0.463415 |  0.0702455  |  0.0687952  |     2.66439 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | 10–15%      |  29 |   0.344828 |  0.121433   |  0.120264   |     2.70793 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | 15–20%      |   8 |   0.25     |  0.175954   |  0.177112   |     3.46875 | COUNTERFACTUAL_NON_PIT |
| FULL            | home_win | >20%        |  13 |   0.230769 |  0.31288    |  0.293765   |     4.81769 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | EV < 0      | 339 |   0.451327 | -0.0532619  | -0.0474825  |     2.28531 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | 0–2%        |  52 |   0.480769 |  0.0107858  |  0.010592   |     2.28385 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | 2–5%        |  48 |   0.583333 |  0.0338632  |  0.0336185  |     2.15563 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | 5–10%       |  34 |   0.264706 |  0.0704723  |  0.0704772  |     3.14382 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | 10–15%      |  13 |   0.384615 |  0.124671   |  0.125373   |     4.01769 | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | 15–20%      |   4 |   0        |  0.163499   |  0.158911   |     5.6125  | COUNTERFACTUAL_NON_PIT |
| MARKET          | home_win | >20%        |  10 |   0.1      |  0.317748   |  0.308918   |     7.3     | COUNTERFACTUAL_NON_PIT |
| MARKET_ONLY     | home_win | EV < 0      | 500 |   0.442    | -0.0634532  | -0.0640255  |     2.50304 | COUNTERFACTUAL_NON_PIT |

**Resultado:** não há monotonicidade robusta entre EV estimado e resultado posterior. Nos modelos Robo, os buckets de EV mais altos não apresentam melhora consistente de win rate/retorno. Portanto:

```text
EV_SIGNAL = WEAK / NOT_PROMOTED
```

## 6. Divergência Robo × mercado

| configuration   | target   | divergence_bucket   |   n |   win_rate |   mean_divergence |   mean_odds | status                        |
|:----------------|:---------|:--------------------|----:|-----------:|------------------:|------------:|:------------------------------|
| BASELINE        | home_win | 0–2pp               | 103 |   0.417476 |       0.000471572 |     2.24806 | PREDICTIVE_DIVERGENCE_NON_PIT |
| BASELINE        | home_win | 2–5pp               | 128 |   0.5      |      -0.00168822  |     2.12891 | PREDICTIVE_DIVERGENCE_NON_PIT |
| BASELINE        | home_win | 5–10pp              | 173 |   0.421965 |       0.0350892   |     2.61457 | PREDICTIVE_DIVERGENCE_NON_PIT |
| BASELINE        | home_win | 10–15pp             |  64 |   0.390625 |       0.0646636   |     2.89406 | PREDICTIVE_DIVERGENCE_NON_PIT |
| BASELINE        | home_win | >15pp               |  32 |   0.5      |       0.0991      |     3.43531 | PREDICTIVE_DIVERGENCE_NON_PIT |
| FULL            | home_win | 0–2pp               | 166 |   0.439759 |       0.000681218 |     2.70892 | PREDICTIVE_DIVERGENCE_NON_PIT |
| FULL            | home_win | 2–5pp               | 199 |   0.427136 |       0.010301    |     2.51497 | PREDICTIVE_DIVERGENCE_NON_PIT |
| FULL            | home_win | 5–10pp              | 117 |   0.470085 |       0.0320391   |     2.25308 | PREDICTIVE_DIVERGENCE_NON_PIT |
| FULL            | home_win | 10–15pp             |  17 |   0.470588 |       0.100821    |     2.06588 | PREDICTIVE_DIVERGENCE_NON_PIT |
| FULL            | home_win | >15pp               |   1 |   0        |       0.16293     |     2.63    | PREDICTIVE_DIVERGENCE_NON_PIT |
| MARKET          | home_win | 0–2pp               | 232 |   0.409483 |       0.0026627   |     2.52578 | PREDICTIVE_DIVERGENCE_NON_PIT |
| MARKET          | home_win | 2–5pp               | 211 |   0.473934 |       0.0266875   |     2.52815 | PREDICTIVE_DIVERGENCE_NON_PIT |
| MARKET          | home_win | 5–10pp              |  57 |   0.45614  |       0.0587901   |     2.31754 | PREDICTIVE_DIVERGENCE_NON_PIT |

As divergências maiores não demonstram uma relação monotônica robusta com resultado. A divergência permanece `RESEARCH_ONLY`.

## 7. Walk-forward secundário

Protocolo exploratório: `min_train=1000`, `validation=200`, `test=300`, holdout final de 15%, quatro folds. Não é diretamente comparável à janela principal do Ciclo 2; serve para verificar se o sinal de seleção sobrevive a múltiplas janelas.

| configuration   | threshold   |   folds |   bets |   units |   mean_fold_roi |   median_fold_roi |   positive_folds |   max_fold_drawdown | status                 |
|:----------------|:------------|--------:|-------:|--------:|----------------:|------------------:|-----------------:|--------------------:|:-----------------------|
| BASELINE        | EV>0        |       4 |    576 |  -69.77 |      -0.120056  |        -0.0800998 |                0 |               41.79 | COUNTERFACTUAL_NON_PIT |
| BASELINE        | EV>10%      |       4 |    378 |  -76.59 |      -0.19903   |        -0.184563  |                0 |               39.5  | COUNTERFACTUAL_NON_PIT |
| BASELINE        | EV>5%       |       4 |    473 |  -76.5  |      -0.16078   |        -0.116143  |                0 |               41.57 | COUNTERFACTUAL_NON_PIT |
| FULL            | EV>0        |       4 |    495 |  -33.41 |      -0.0784067 |        -0.053381  |                1 |               27.41 | COUNTERFACTUAL_NON_PIT |
| FULL            | EV>10%      |       4 |    136 |  -24.29 |      -0.267995  |        -0.417989  |                1 |               25    | COUNTERFACTUAL_NON_PIT |
| FULL            | EV>5%       |       4 |    287 |   -4.66 |      -0.0351318 |        -0.0502593 |                2 |               22.89 | COUNTERFACTUAL_NON_PIT |
| MARKET          | EV>0        |       4 |    404 |  -28.7  |      -0.0539846 |        -0.0831328 |                1 |               40.58 | COUNTERFACTUAL_NON_PIT |
| MARKET          | EV>10%      |       4 |     76 |  -10.84 |      -0.182973  |        -0.195328  |                2 |               16.05 | COUNTERFACTUAL_NON_PIT |
| MARKET          | EV>5%       |       4 |    180 |  -20.86 |      -0.101914  |        -0.0793571 |                1 |               22.73 | COUNTERFACTUAL_NON_PIT |
| MARKET_ONLY     | EV>0        |       4 |      0 |    0    |     nan         |       nan         |                0 |                0    | COUNTERFACTUAL_NON_PIT |
| MARKET_ONLY     | EV>10%      |       4 |      0 |    0    |     nan         |       nan         |                0 |                0    | COUNTERFACTUAL_NON_PIT |
| MARKET_ONLY     | EV>5%       |       4 |      0 |    0    |     nan         |       nan         |                0 |                0    | COUNTERFACTUAL_NON_PIT |

**Achado crítico:** o `ROBO_BASELINE` teve `0/4` folds positivos em `EV>0`; `ROBO + MARKET` teve apenas `1/4`; `FULL` teve `1/4` em `EV>0` e 2/4 em alguns thresholds, mas com retorno agregado negativo. Isso elimina a hipótese de promover a seleção observada no primeiro fold.

## 8. Stake Engine

O teto permanece:

```text
2U = HARD CEILING
```

No common sample, a regra dinâmica experimental atribuiu apenas `0,25U` às oportunidades aprovadas em `EV>5%`; não houve evidência suficiente para justificar `0,50U`, `1U`, `1,5U` ou `2U`. Isso é coerente com uma política conservadora, mas **não demonstra que 0,25U seja o sizing ótimo**.

| configuration   | selection   | stake_strategy   |   bets |    units |          roi |   max_drawdown_u |   profit_factor |   win_rate |   avg_odds |   longest_losing_streak |   volatility | scientific_status      |
|:----------------|:------------|:-----------------|-------:|---------:|-------------:|-----------------:|----------------:|-----------:|-----------:|------------------------:|-------------:|:-----------------------|
| MARKET_ONLY     | STRICT      | flat_1.0         |      0 |   0      | nan          |           0      |      nan        | nan        |  nan       |                     nan |   nan        | COUNTERFACTUAL_NON_PIT |
| MARKET_ONLY     | STRICT      | dynamic          |      0 |   0      | nan          |           0      |      nan        | nan        |  nan       |                     nan |   nan        | COUNTERFACTUAL_NON_PIT |
| BASELINE        | STRICT      | flat_1.0         |    204 |  -0.43   |  -0.00210784 |          16.77   |        0.996742 |   0.352941 |    3.33069 |                       8 |     1.45225  | COUNTERFACTUAL_NON_PIT |
| BASELINE        | STRICT      | dynamic          |    204 |  -0.1075 |  -0.00210784 |           4.1925 |        0.996742 |   0.352941 |    3.33069 |                       8 |     0.363062 | COUNTERFACTUAL_NON_PIT |
| MARKET          | STRICT      | flat_1.0         |     61 | -12.79   |  -0.209672   |          17.34   |        0.721957 |   0.245902 |    4.17328 |                       9 |     1.53845  | COUNTERFACTUAL_NON_PIT |
| MARKET          | STRICT      | dynamic          |     61 |  -3.1975 |  -0.209672   |           4.335  |        0.721957 |   0.245902 |    4.17328 |                       9 |     0.384614 | COUNTERFACTUAL_NON_PIT |
| FULL            | STRICT      | flat_1.0         |     91 | -15.68   |  -0.172308   |          19.86   |        0.724912 |   0.373626 |    3.05659 |                       8 |     1.13623  | COUNTERFACTUAL_NON_PIT |
| FULL            | STRICT      | dynamic          |     91 |  -3.92   |  -0.172308   |           4.965  |        0.724912 |   0.373626 |    3.05659 |                       8 |     0.284058 | COUNTERFACTUAL_NON_PIT |

O sizing não criou edge. Onde a mesma seleção é usada, aumentar stake apenas escala Units e drawdown; não melhora a qualidade da seleção.

## 9. Respostas do CEO

1. **Robo + Market gera melhor seleção que Market-only?** — **Não demonstrado.**
2. **EV possui poder discriminativo?** — **Não robusto.**
3. **Aumentar seletividade melhora ROI?** — **Não de forma estável.**
4. **Número de apostas diminui com filtros?** — **Sim.**
5. **Profit Units melhoram?** — **Não robustamente.**
6. **Drawdown melhora?** — Filtros reduzem exposição e frequentemente drawdown absoluto, mas isso não significa melhor retorno ajustado ao risco.
7. **Sizing dinâmico é melhor que flat?** — **Não comprovado.**
8. **Há evidência para 1U vs 0,5U?** — **Não.**
9. **Há evidência para 1,5U/2U?** — **Não.**
10. **Divergência Robo/mercado tem valor?** — **Research-only; sem evidência robusta.**
11. **Robo adiciona informação independente ao mercado?** — Há melhoria preditiva incremental sobre o Robo baseline, mas o benchmark market-only ainda é melhor em qualidade probabilística.
12. **Está apenas reproduzindo mercado?** — O `ROBO + MARKET` está fortemente dependente da informação de mercado; não há demonstração de valor independente para betting.
13. **Melhor configuração para o próximo ciclo?** — `LOGISTIC + MARKET` permanece o candidato preditivo, mas a **selection layer deve ser reformulada/validada com PIT**, não promovida.

## 10. Decisão

```text
PREDICTION: IMPROVEMENT_PARTIAL
SELECTION: NOT_PROVEN
EV_DISCRIMINATION: WEAK
SIZING: RESEARCH_ONLY
REAL_BETTING_EDGE: NOT_PROVEN
```

**Classificação: C — INCONCLUSIVE.**

O Ciclo 3 foi bem-sucedido como teste científico porque eliminou uma hipótese importante: a melhora de previsão do Ciclo 2, isoladamente, **não é suficiente para gerar seleção de apostas superior**.

## 11. Ciclo 4 recomendado

O gargalo deve voltar para:

```text
EXACT PIT ODDS
→ DECISION SNAPSHOT
→ ENTRY PRICE
→ PAPER BET
→ SETTLEMENT
→ CLOSING PRICE
→ CLV
→ OOS REAL
```

Sem isso, continuar otimizando thresholds e sizing corre risco de otimizar ruído de preços não-PIT. A prioridade do Ciclo 4 deve ser adquirir uma população PIT válida e então repetir a seleção do `LOGISTIC + MARKET` sem mudar o holdout final.
