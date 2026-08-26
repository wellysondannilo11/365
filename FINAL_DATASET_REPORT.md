# FINAL DATASET REPORT

## Fonte primária planejada
PostgreSQL (`v25_dataset_rows`) quando operacional.

## Observações brutas
`v25_observation_snapshots` no PostgreSQL quando operacional, com JSONL como espelho forense/fallback.

## Integridade
- append-only/hash chain: PASS na suíte de engenharia
- deduplicação/idempotência: PASS na suíte disponível
- timestamps PIT: PASS na suíte disponível
- timestamps futuros: rejeitados
- `commence_time` não é usado como `source_timestamp` no adapter real

## Dados reais desta execução
- eventos: **0**
- snapshots: **0**
- decisões: **0**
- BETs: **0**
- NO BET: **0**
- settlements: **0**

Nenhum fixture foi incorporado como evidência real.
