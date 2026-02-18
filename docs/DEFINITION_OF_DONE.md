# Definition of Done (DoD) — LAI Packs

Este documento formaliza o **Definition of Done** por tipo de pack.  
Objetivo: reduzir drift do GPT Builder, garantir manutenção e padronizar gates.

> Regra de ouro: **sem DoD atendido, o pack não promove**.

## DoD — Pack0 (Planejamento Padrão)

Obrigatório no Pack0:

### Documentação
- [ ] `docs/PLAN.md` contém todas as seções do padrão SRS:
  - [ ] Introdução (Propósito, Escopo, Usuários, Referências)
  - [ ] Visão Geral do Produto (Perspectiva, Funcionalidades, Ambiente, Limitações, Suposições/Dependências)
  - [ ] Requisitos Funcionais (RF) — lista numerada e testável
  - [ ] Requisitos Não Funcionais (RNF) — lista numerada e mensurável
  - [ ] Casos de Uso (UC) — ao menos o thin-slice E2E
  - [ ] Diagramas (arquitetura, sequência/iteração, classes quando aplicável)
  - [ ] Rastreabilidade (RF/RNF → Contratos → Testes)
  - [ ] Riscos, Rollout e Rollback
- [ ] `docs/PROMPT_CONTINUIDADE.md` (estado atual + próximos passos)
- [ ] `docs/TROUBLESHOOTING.md` (erros esperados e correção padrão)

### Estrutura mínima (pack-first)
- [ ] `/contracts` existe (mesmo que com placeholders)
- [ ] `/infra` existe
- [ ] `/db/migrations` e `/db/seeds` existem (mesmo que vazios)
- [ ] `/observability` existe (placeholders ok)
- [ ] `/tests` existe (skeleton ok)
- [ ] `/runbooks/HOW_TO_RUN.md`, `HOW_TO_DEPLOY.md`, `HOW_TO_ROLLBACK.md`
- [ ] `/history` existe (append-only: incidents/changes)

### Gates (objetivos)
- [ ] `lai-pack validate-pack0` passa **sem lacunas críticas**  
  (ou lacunas ficam explicitamente registradas como “não aplicável” com justificativa).

## DoD — Pack1 (Thin-slice Executável)

Obrigatório no Pack1:

### Código + Execução
- [ ] Um thin-slice E2E rodando localmente (`make up`)
- [ ] Config por `.env.example` + defaults seguros
- [ ] Healthcheck/Readiness básico

### Contratos
- [ ] Schemas CloudEvents/DTOs do módulo versionados em `/contracts`
- [ ] Eventos críticos com `tenant_id`, `actor_id`, `trace_id`

### Observabilidade e auditoria
- [ ] Logs estruturados
- [ ] Traces (placeholder ok, mas instrumentado)
- [ ] Audit log append-only para ações críticas

### Testes
- [ ] Unit: regras/validações principais
- [ ] Integration: contrato/evento e persistência
- [ ] E2E: thin-slice completo

### Runbooks
- [ ] HOW_TO_RUN atualizado
- [ ] HOW_TO_DEPLOY + HOW_TO_ROLLBACK executáveis
- [ ] Troubleshooting com erros mais prováveis

## DoD — PackX.Y (Correção / Incremento)

Obrigatório no PackX.Y:

- [ ] OCA-REPORT ou OCA-PATCH preenchido (sem “texto solto”)
- [ ] Testes atualizados ou justificativa explícita
- [ ] Merge gera novo snapshot
- [ ] Software Book atualizado automaticamente (no merge)

## DoD — Merge / Snapshot

Quando rodar `lai-pack merge`:

- [ ] Merge determinístico (ordem de entrada importa e é registrada)
- [ ] `docs/public/FILEMAP.md` gerado
- [ ] `docs/public/SOFTWARE_BOOK.md` gerado/atualizado
- [ ] Nenhuma violação append-only em `history/`

