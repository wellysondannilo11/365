# MISSÃO ESPECIALISTA — TRANSFERÊNCIA DE CONTEXTO

## O que mudou

O Robo agora possui uma camada formal de transferência de evidência entre competições.

### Hierarquia
1. competição específica;
2. temporada atual/mais recente e outras competições oficiais;
3. forma recente 3/5/10/20;
4. histórico ampliado com decaimento temporal.

### Proteções
- `DIRECT_EVIDENCE` e `TRANSFERRED_EVIDENCE` ficam separados;
- `MODEL_PROBABILITY`, `MODEL_CONFIDENCE` e `EDGE` são independentes;
- transferência reduz confiança;
- nenhuma informação futura entra nas características históricas;
- feminino e masculino permanecem separados;
- `DATE_LEVEL_PIT` nunca vira `VALUE_BET`;
- dinheiro real continua desabilitado;
- snapshots prospectivos não são sobrescritos.

## Resultado desta execução

- 4.864 jogos históricos preservados;
- 8 competições;
- 9 temporadas;
- 368 equipes normalizadas;
- 10 clubes do piloto avaliados;
- 2 clubes com evidência transferível individual (Santos e Corinthians);
- 0 partidas do piloto plenamente analisáveis por transferência, porque o outro lado dos confrontos continua sem massa suficiente no dataset materializado;
- transferência entre competições: `NOT_VALIDATED` como ganho científico, pois apenas 5 clubes aparecem em mais de uma competição no conjunto atual;
- aquisição externa nova: 0 bytes, bloqueada por DNS;
- novos PIT: 0;
- VALUE_BET: 0;
- dinheiro real: DESABILITADO.

## Pesquisa OOS

Divisão temporal 70/30 sobre os dados materializados:

- Frequência histórica: Brier 0,655375; Log Loss 1,081772
- Sinal direto da competição: Brier 0,626368; Log Loss 1,041635
- Transferência contextual: Brier 0,625267; Log Loss 1,040059

O pequeno ganho é apenas descritivo. Não constitui edge e não promove nenhuma feature para apostas.

## Aquisição

O ambiente desta execução apresentou `Temporary failure in name resolution` para as rotas externas testadas. Portanto, nenhuma fonte externa encontrada foi convertida em dado empírico novo.
