# PROMPT — PACK0 (Planejamento Padrão)
**trace_id:** LAI-V009-6F8570C9

## Regra de comunicação
300 Franchising, a maior do mundo e nossa missão

### Comando
Gere um RELEASE PACK **Pack0** para o módulo informado (ex.: `meetcore`, `connect`, `app`, `culture-people`).

### Regras obrigatórias
1) Siga `gpt_builder/ORQUESTRADOR_MASTER.md` e `gpt_builder/MODO_EXECUCAO_PADRAO_LAI.md`.  
2) Pack0 é **planejamento** (SRS), não código de produção (pode conter scaffolds e contratos placeholders).
3) Pack0 deve conter **100% do padrão SRS**:
   - Introdução, Visão Geral, RF, RNF, UC, Diagramas, Rastreabilidade, Plano, Testes, Aceite, Rollout, Rollback, DoD.
4) Gate objetivo:
   - O Pack0 só está “pronto” se passar no `validate-pack0` (ou registrar explicitamente o que não se aplica, com justificativa).

### Entrega mínima (pack-first)
- `/contracts` (CloudEvents + DTOs + schema_version)
- `/docs/PLAN.md` (SRS completo)
- `/docs/DEFINITION_OF_DONE.md`
- `/docs/PROMPT_CONTINUIDADE.md`
- `/docs/TROUBLESHOOTING.md`
- `/runbooks/HOW_TO_RUN.md`, `/runbooks/HOW_TO_DEPLOY.md`, `/runbooks/HOW_TO_ROLLBACK.md`
- `/tests` (skeleton unit/integration/e2e + plano mapeado a RF/RNF)
- `/infra` (docker-compose mínimo + env.example)
- `/SECURITY.md` + `/CHANGELOG.md`
- `/history` append-only (inicial)
- manifesto (`02_INVENTORY/manifest.json`) + metadados (`02_INVENTORY/pack.meta.json`)

### Saída
- Um ZIP do Pack0.



### Nota (MeetCore)
- Se module=meetcore, incluir seção de alta complexidade (thin-slices PEC1.01..PEC1.05, budgets SLO/SLI, contratos meetcore.*).


## Nota específica — MeetCore
Se o módulo for **meetcore**, o Pack0 deve incluir explicitamente:
- `docs/MEETCORE_SLICES.md` (deve citar PEC1.01..PEC1.05)
- `docs/PERFORMANCE_BUDGETS.md` (deve citar 300ms)
- `docs/DATA_RETENTION_MATRIX.md` (deve mencionar Culture & People pipeline efêmero)
