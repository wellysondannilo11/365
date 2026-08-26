# V8 AQUISIÇÃO

## Resultado
- Remote bytes acquired: **0**
- Local bytes reused for real materialization: **98,906**
- New canonical matches: **953**
- Libertadores: **889**
- Brasileirão Série A 2024: **64**

## Bloqueio remoto
O container não resolve DNS (`raw.githubusercontent.com`, `github.com` etc.). O teste HTTP confirmou `curl: (6) Could not resolve host`. Portanto nenhuma fonte remota foi promovida a adquirido.

## Regra aplicada
DISCOVERED != ACQUIRED != MATERIALIZED. Apenas arquivos que já existiam dentro do ZIP foram usados para fechar gaps nesta execução.
