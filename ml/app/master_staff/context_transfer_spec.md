# Especificação — Transferência de Contexto

## Objetivo
Permitir análise pré-jogo quando a competição específica possui pouca massa, usando evidência transferível do mesmo clube sem confundir essa evidência com prova de valor.

## Hierarquia
1. Competição específica.
2. Temporada e outras competições oficiais.
3. Forma recente (3/5/10/20).
4. Histórico ampliado com decaimento temporal.

## Regras
- Cada peso fica em `TRANSFER_CONFIG.json`.
- A origem da evidência é registrada.
- `TRANSFERRED_EVIDENCE` reduz a confiança.
- Probabilidade, confiança e edge são campos independentes.
- Ausência de PIT válido bloqueia `VALUE_BET`.
- Gênero masculino/feminino nunca é misturado.
- Nenhuma característica pode ter timestamp posterior ao `decision_timestamp`.

## Validação
A transferência somente poderá ser promovida a componente de produção após validação fora da amostra/walk-forward. A execução atual é pesquisa e diagnóstico.
