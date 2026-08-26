# Local Data Acquisition — Robo da Bet

## Objetivo

Permitir aquisição histórica legítima em uma máquina com internet normal, sem depender do ambiente restrito da IA.

## Pipeline

`FOUND → ACCESSIBLE → DOWNLOAD_STARTED → DOWNLOADED → CHECKSUM_VALIDATED → MATERIALIZED → NORMALIZED → VALIDATED → PROCESSED → USED_IN_MODEL`

Falhas: `FAILED` / `BLOCKED`.

## Execução

Na raiz do projeto:

```bash
python scripts/global/data_acquisition_worker.py --config config/data_acquisition_local.json --url "https://.../arquivo.csv"
```

Para uma fonte local:

```bash
python scripts/global/data_acquisition_worker.py --config config/data_acquisition_local.json --path "/caminho/arquivo.csv"
python scripts/global/local_materializer.py
```

A configuração aceita `data_root`, `raw_root`, `processed_root`, `cache_root`, `log_root`, timeout, retries e uma lista `sources`.

## Regras

- Não há bypass de Cloudflare, autenticação, robots, paywall ou controles de acesso.
- Credenciais nunca ficam hardcoded.
- Arquivos existentes com SHA-256 idêntico são reutilizados.
- Downloads são atômicos (`.part` + rename).
- O worker não promove automaticamente `DOWNLOADED` para `MATERIALIZED`.
- Timestamp ausente não é convertido artificialmente em Exact PIT.
- `REAL_MONEY = DISABLED`.
