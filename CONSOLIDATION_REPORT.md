# ROBO DA BET — RELATÓRIO DE CONSOLIDAÇÃO FÍSICA

## 1. Objetivo e método

Foram analisados cinco snapshots físicos fornecidos no pacote de recuperação. A consolidação foi feita por comparação de caminhos relativos e SHA-256 dos arquivos, excluindo artefatos gerados (`target`, `node_modules`, `.git`, `.pytest_cache`, `__pycache__` e `.pyc`).

A regra aplicada foi:

1. usar o C18 como base estrutural porque ele é o snapshot completo mais recente e contém a camada C18;
2. preservar integralmente funcionalidades que existem somente no C16;
3. manter arquivos idênticos sem duplicação;
4. resolver os únicos cinco conflitos de caminho usando evidência funcional/temporal, não o nome do diretório;
5. não recriar código nem transformar relatórios em implementação;
6. não modificar a baseline V8.

## 2. Snapshots analisados

| Snapshot | Arquivos auditados* | Observação |
|---|---:|---|
| C16 | 1.383 | Contém material exclusivo de C15/C16, além da base comum |
| C17 | 1.331 | Estrutura comum; não possui arquivos exclusivos após normalização |
| C18 | 1.368 | Snapshot mais recente da linha C16–C18; base escolhida |
| V16 Cycle 2 | 1.260 | Candidate de pesquisa; sem arquivos exclusivos após normalização |
| V16 Cycle 3 | 1.279 | Candidate de pesquisa; sem arquivos exclusivos após normalização |

\* Contagem sem caches, `target`, `node_modules`, `.git`, `.pytest_cache`, `__pycache__` e `.pyc`.

## 3. Decisão estrutural

**Base funcional:** C18.

**Complemento obrigatório:** arquivos exclusivos do C16.

Isso evita perder os módulos e artefatos de C15/C16 que não aparecem no C18, ao mesmo tempo em que preserva C18 como estado mais avançado da linha recente.

C17, V16 Cycle 2 e V16 Cycle 3 não acrescentaram caminhos de código exclusivos após normalização. Eles foram úteis como referências de comparação e validação de continuidade.

## 4. Conflitos de implementação/artefatos

Foram encontrados exatamente cinco caminhos presentes nos cinco snapshots com conteúdos diferentes:

1. `artifacts/paper_trading/v21_event_ledger.jsonl`
2. `artifacts/paper_trading/v21_research.jsonl`
3. `data/global_dataset/registry/DATA_ACQUISITION_MANIFEST.json`
4. `reports/free_enrichment_v5/GLOBAL_ENRICHMENT_STATUS_V5.json`
5. `reports/free_enrichment_v5/NETWORK_PROBE.json`

### 4.1 Ledger V21

O C18 foi preservado porque contém o prefixo integral comum do C17 e registros adicionais posteriores. O C18 possui 150 registros, contra 147 no C17 e 149 no C16. O prefixo C17 é idêntico ao C18 nos 147 registros existentes. Portanto, a escolha não foi baseada apenas no nome do snapshot: houve evidência de que o C18 representa uma extensão temporal do ledger.

### 4.2 Research ledger V21

Mesma conclusão: C18 possui 150 registros e preserva integralmente o prefixo comum do C17, acrescentando registros posteriores.

### 4.3 Manifesto de aquisição

O C18 possui o maior conteúdo do manifesto entre os snapshots conflitantes e representa a execução mais recente da mesma estrutura de aquisição. Foi preservado integralmente.

### 4.4 Status de enriquecimento e probe

Os cinco arquivos têm a mesma estrutura, mas timestamps de execução diferentes. O C18 contém o timestamp mais recente entre os cinco snapshots (`2026-08-24T22:00...Z`). O C18 foi mantido para preservar o estado observacional mais recente.

## 5. Funcionalidades recuperadas

A consolidação preserva, onde fisicamente existente no código:

- engine de decisão e seleção;
- pricing;
- fair odds;
- de-vig;
- EV/edge;
- consenso de mercado;
- market intelligence;
- modelos e módulos de ML;
- V19/V20/V21/V22/V24/V25;
- PIT e controles temporais;
- `observation_id` e `decision_id`;
- ledger imutável/hash-chain;
- paper/shadow trading;
- settlement;
- CLV;
- risk/kill switch;
- exportação XLSX;
- adapters/provedores de odds, incluindo integração The Odds API;
- pesquisa C15/C16/C17/C18;
- scripts de aquisição e enriquecimento;
- datasets e manifestos;
- backend Spring Boot;
- frontend React/Vite;
- Docker/Compose;
- SQL/migrations;
- testes Python;
- documentação e relatórios científicos.

A presença de uma funcionalidade na lista acima significa que há implementação/documentação correspondente no snapshot físico; não significa que a funcionalidade tenha sido cientificamente validada para dinheiro real.

## 6. Regras de apostas preservadas

A auditoria local encontrou referências implementadas/documentadas para regras de preço e seleção, incluindo:

- preferência por odds a partir de 1,66 em módulos recentes;
- bloqueio de odds abaixo de 1,50;
- tratamento excepcional da faixa 1,50–1,65;
- seleção de mercado orientada por valor;
- fair probability/fair odds;
- de-vig;
- EV/edge;
- stake e unidades;
- BET/NO BET;
- ranking/seleção;
- `MAX_TIPS`;
- registro de P&L;
- paper/shadow;
- CLV;
- kill switch;
- `REAL_MONEY = DISABLED`.

Essas regras foram preservadas; nenhuma foi reotimizada durante a consolidação.

## 7. PIT e temporalidade

O projeto consolidado contém múltiplas camadas de PIT, incluindo validação de timestamps, `observation_id`, `decision_id`, provenance e gates que bloqueiam evidência temporal inválida. A pesquisa C15/C16/C17/C18 permanece segregada de dados NON-PIT.

A consolidação não promoveu nenhum timestamp de arquivo/download/recebimento a `provider_timestamp`.

## 8. Providers e integração

A camada Python possui abstração de providers e integração The Odds API, além dos componentes de pesquisa/adapters associados aos ciclos. O `docker-compose.yml` configura o serviço `ml` na porta 8001 e o backend Java na porta 8080.

O backend Spring atua como gateway para o serviço ML e expõe endpoints de saúde, pesquisa, V20, V21, V22, V24 e V25.

## 9. Backend

Todos os snapshots apontam para:

- `groupId = com.robobet`
- `artifactId = robobet-api`
- `version = 25.0.0`
- Spring Boot `3.5.4`
- Java `21`

O backend possui três classes Java principais e não foram encontradas classes Java duplicadas no mesmo caminho lógico.

Não houve alteração de arquitetura Java durante a consolidação; os arquivos do C18 foram preservados.

## 10. Frontend

O frontend contém React/Vite, `package.json`, Dockerfile e teste Node nativo. O teste frontend foi executado com sucesso:

- 2 testes coletados;
- 2 PASS;
- 0 FAIL.

O build Vite não foi executado porque as dependências locais (`node_modules`) não estavam presentes e não foi feita instalação de dependências durante esta recuperação.

## 11. Python/ML

`python -m compileall -q ml` foi executado e terminou com código 0.

A suíte Python foi coletada com **302 testes**. A execução integral `pytest -q` foi iniciada, mas excedeu o timeout do ambiente; portanto o resultado integral é **TIMEOUT**, não PASS.

Foram executados batches direcionados cobrindo os ciclos e famílias principais. Os batches executados terminaram com PASS, incluindo:

- C15;
- C16;
- C17;
- C18;
- V5;
- V16;
- V21;
- V22;
- V23;
- V24;
- V25;
- V11–V20;
- master_staff;
- expansion;
- free enrichment;
- conmebol;
- round scan;
- research cycles 2–4.

Não foi declarado PASS para a suíte integral.

## 12. Maven

O ambiente de execução possui Java 21, porém **não possui o comando `mvn` nem Maven Wrapper no snapshot**. Assim:

- `mvn test`: **NÃO EXECUTADO — ferramenta Maven ausente**;
- compilação Maven: **NÃO VERIFICADA**;
- não foi inventado resultado de build.

Isso é um blocker de verificação do ambiente, não uma evidência de erro de compilação do código.

## 13. Docker

Existe configuração Docker real:

- `docker-compose.yml`;
- `backend/Dockerfile`;
- `ml/Dockerfile`;
- `frontend/Dockerfile`.

O comando Docker não está disponível neste ambiente, portanto o build dos containers não foi executado.

## 14. Caminhos absolutos e artefatos históricos

Foi encontrada referência histórica a caminhos absolutos `/mnt/data/...` em manifestos e relatórios. Essas referências pertencem a registros de proveniência/execução históricos e não foram reescritas, porque alterar esses artefatos mudaria a evidência histórica.

Também existem scripts com diretórios de trabalho absolutos, por exemplo em `ml/scripts/expand_real_datasets.py` e `scripts/global/run_global_dataset_enrichment.py`. Eles devem ser tratados como **warning de portabilidade** e não foram alterados automaticamente por não haver evidência suficiente de que a alteração seria apenas de consolidação.

Não foram encontradas referências a `C:\Users\...` nos arquivos consolidados.

## 15. Arquivos descartados

Somente conteúdos descartáveis foram excluídos do material físico: caches, `target`, `node_modules`, `.pytest_cache`, `__pycache__` e `.pyc`.

Nos conflitos de cinco caminhos, as versões não-C18 foram descartadas do arquivo consolidado porque eram estados alternativos do mesmo artefato; todas estão documentadas em `FILE_PROVENANCE.csv`.

Nenhum módulo de código exclusivo foi descartado.

## 16. Arquivos mesclados

A consolidação foi uma união física por caminho relativo:

- C18 forneceu a base;
- 88 caminhos exclusivos do C16 foram recuperados;
- 37 caminhos exclusivos do C18 já estavam na base;
- C17, V16C2 e V16C3 não possuíam caminhos exclusivos após normalização;
- os cinco conflitos foram resolvidos conforme a seção 4.

## 17. Quantidade final

Após a consolidação e antes da criação deste relatório/protocolo, havia **1.458 arquivos físicos** recuperados/gerados no projeto consolidado.

Com `CONSOLIDATION_REPORT.md`, `RECOVERY_STATUS.md` e `FILE_PROVENANCE.csv`, a entrega final contém **1.461 arquivos**, sem caches e artefatos de build descartáveis.

## 18. Confiança

**Nível de confiança: ALTO para recuperação estrutural e funcional; MÉDIO para validação operacional completa.**

Motivos:

- os cinco snapshots foram comparados fisicamente;
- não foram necessárias reconstruções por memória;
- conflitos de implementação foram identificados de forma objetiva;
- todos os módulos exclusivos relevantes foram preservados;
- `compileall` passou;
- testes direcionados passaram;
- frontend test passou;
- Maven e Docker não puderam ser executados por ausência das ferramentas no ambiente;
- a suíte Python integral excedeu o timeout.

## 19. Conclusão

O projeto consolidado representa o melhor estado recuperável dos cinco snapshots sem sobrescrever funcionalidades exclusivas importantes e sem fabricar implementação.

Classificação de recuperação: **RECOVERED_WITH_WARNINGS**.

O principal motivo para não classificar como `RECOVERED` pleno é a ausência de execução verificável do build Maven/Docker e o timeout da suíte Python integral.

`REAL_MONEY = DISABLED` permanece preservado.
