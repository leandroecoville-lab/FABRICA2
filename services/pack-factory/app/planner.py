from __future__ import annotations
import zipfile
import re
from pathlib import Path
from .manifest import new_manifest, write_manifest
from .utils import ensure_dir, write_json

def generate_pack0(module: str, out_dir: Path, trace_id: str) -> Path:
    pack_id = f"pack0-{module}"
    version = "0.0.1"
    pack_root = out_dir / f"{pack_id}-{version}"
    if pack_root.exists():
        import shutil
        shutil.rmtree(pack_root)
    ensure_dir(pack_root)

    for d in [
        "00_INDEXES","02_INVENTORY","contracts","services","infra","db/migrations","db/seeds",
        "observability/dashboards","tests/unit","tests/integration","tests/e2e","runbooks","docs",
        "history/incidents","history/changes","gpt_builder"
    ]:
        ensure_dir(pack_root / d)

    (pack_root / "00_INDEXES" / "README.md").write_text(
        f"# 300 Franchising, a maior do mundo e nossa missão\n\nPack0 (Planejamento) — módulo: {module}\n",
        encoding="utf-8"
    )
    (pack_root / "docs" / "PLAN.md").write_text(_plan_template(module, trace_id), encoding="utf-8")
    (pack_root / "docs" / "PROMPT_CONTINUIDADE.md").write_text(_continuity_template(module), encoding="utf-8")
    (pack_root / "docs" / "TROUBLESHOOTING.md").write_text(_troubleshooting_template(), encoding="utf-8")
    (pack_root / "docs" / "DEFINITION_OF_DONE.md").write_text(_dod_template(), encoding="utf-8")


    # Artefatos explícitos por módulo (evita drift; facilita manutenção)
    mod = module.strip().lower()
    mod_key = re.sub(r"[^a-z0-9]+", "-", mod).strip("-")

    # Governança de dados (sempre): retenção e minimização por módulo
    (pack_root / "docs" / "DATA_RETENTION_MATRIX.md").write_text(_data_retention_matrix_template(), encoding="utf-8")

    # MeetCore-first: slices + budgets
    if mod_key == "meetcore":
        (pack_root / "docs" / "MEETCORE_SLICES.md").write_text(_meetcore_slices_template(), encoding="utf-8")
        (pack_root / "docs" / "PERFORMANCE_BUDGETS.md").write_text(_meetcore_budgets_template(), encoding="utf-8")

    # LAI Connect: slices (omnicanal + integrações)
    if mod_key in ("lai-connect", "connect", "lai-connect-mvp"):
        (pack_root / "docs" / "CONNECT_SLICES.md").write_text(_connect_slices_template(), encoding="utf-8")

    # App LAI: slices (experiência unificada + feed + rotinas)
    if mod_key in ("app-lai", "app", "lai-app"):
        (pack_root / "docs" / "APP_LAI_SLICES.md").write_text(_app_lai_slices_template(), encoding="utf-8")

    # Culture & People: slices (pipeline efêmero + vetores + guidance)
    if mod_key in ("culture-people", "culture", "lai-culture", "culture-and-people"):
        (pack_root / "docs" / "CULTURE_PEOPLE_SLICES.md").write_text(_culture_people_slices_template(), encoding="utf-8")

    entrypoints = ["docs/PLAN.md", "docs/DEFINITION_OF_DONE.md", "docs/DATA_RETENTION_MATRIX.md"]
    if mod_key == "meetcore":
        entrypoints += ["docs/MEETCORE_SLICES.md", "docs/PERFORMANCE_BUDGETS.md"]
    if mod_key in ("lai-connect", "connect", "lai-connect-mvp"):
        entrypoints += ["docs/CONNECT_SLICES.md"]
    if mod_key in ("app-lai", "app", "lai-app"):
        entrypoints += ["docs/APP_LAI_SLICES.md"]
    if mod_key in ("culture-people", "culture", "lai-culture", "culture-and-people"):
        entrypoints += ["docs/CULTURE_PEOPLE_SLICES.md"]
    m = new_manifest(pack_id=pack_id, version=version, modules=[module], entrypoints=entrypoints, trace_id=trace_id)
    write_manifest(pack_root, m)

    write_json(pack_root / "contracts" / "README.json", {"module": module, "note": "Coloque aqui schemas CloudEvents/DTOs do módulo."})

    (pack_root / "runbooks" / "HOW_TO_RUN.md").write_text(_how_to_run_template(module), encoding="utf-8")
    (pack_root / "runbooks" / "HOW_TO_DEPLOY.md").write_text(_how_to_deploy_template(module), encoding="utf-8")
    (pack_root / "runbooks" / "HOW_TO_ROLLBACK.md").write_text(_how_to_rollback_template(module), encoding="utf-8")

    out_zip = out_dir / f"{pack_id}-{version}.zip"
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in pack_root.rglob("*"):
            if p.is_dir():
                continue
            z.write(p, p.relative_to(pack_root).as_posix())
    return out_zip

def _plan_template(module: str, trace_id: str) -> str:
    # Template alinhado ao documento_de_requisitos_analise_projeto.pdf (SRS)
    base = f"""# Pack0 — Planejamento Padrão ({module})

**trace_id:** {trace_id}

> Este Pack0 é um *artefato de planejamento* (não entrega código executável).
> Ele existe para virar a fonte de verdade do Pack1.

---

## 1 Introdução

### 1.1 Propósito
Definir o planejamento padronizado (SRS) do módulo **{module}**, com requisitos, casos de uso, rastreabilidade e gates.

### 1.2 Escopo
- Dentro do escopo: thin-slice E2E do módulo {module} + contratos + testes + runbooks.
- Fora do escopo (por enquanto): tudo que não for necessário para o thin-slice validável.

### 1.3 Características dos Usuários
Perfis (exemplos):
- Operação / Suporte (debug e rollback)
- Admin (configuração e segurança)
- Usuário final (fluxo do produto)

### 1.4 Referências
- Documento de Requisitos (SRS) — `docs/references/documento_de_requisitos_analise_projeto.pdf`
- Estudos GitHub / inspiração — `docs/references/`
- Blueprints do ecossistema LAI (Fonte interna: Pack)
- MeetCore — `docs/references/25.pdf`
- LAI Connect — `docs/references/Lai Connect - blueprint confidencial.pdf`
- App LAI — `docs/references/App lai blueprint - confidencial.pdf` e `docs/references/App Lai - sistema Lai resumo.pdf`
- Culture & People — `docs/references/Lai Culture & People documentacao tecnica.pdf`
- Dicionário de termos sensíveis — `docs/references/LAI_REINTERPRETACAO_BIG_TECH_v2.0.md`

---

## 2 Visão Geral do Produto

### 2.1 Perspectiva do Produto
Como o módulo {module} se integra aos demais módulos (event bus, contratos, observabilidade, auditoria).

### 2.2 Funcionalidades (resumo)
- RF-001: Definir um fluxo E2E mínimo do módulo {module}
- RF-002: Publicar/consumir eventos (quando aplicável)
- RF-003: Persistência mínima (quando aplicável)

### 2.3 Ambiente Operacional
- Local: docker-compose
- CI: execução de testes unit/integration/e2e
- Observabilidade: logs estruturados + traces (placeholder ok)

### 2.4 Limitações
- Limites atuais do GPT Builder (ex.: unzip, tamanho, tempo) e mitigação via packs/snapshots.

### 2.5 Suposições e Dependências
- Dependência de contratos versionados
- Dependência de infraestrutura (fila, db, etc.)

---

## 3 Requisitos Funcionais (RF)

> Todo RF deve ser testável e rastreável.

| ID | Descrição | Critério de Aceite | Contratos | Testes |
|---|---|---|---|---|
| RF-001 | Thin-slice E2E do módulo {module} | fluxo roda local sem intervenção | contracts/* | tests/e2e/* |
| RF-002 | Evento(s) críticos com trace_id | evento validado por schema | contracts/events/* | tests/integration/* |
| RF-003 | Logs estruturados | logs com correlação | — | tests/smoke/* |

---

## 4 Requisitos Não Funcionais (RNF)

| ID | Descrição | Métrica/Alvo | Evidência |
|---|---|---|---|
| RNF-001 | Observabilidade mínima | logs + trace placeholder | observability/* |
| RNF-002 | Segurança mínima | RBAC/TBAC + audit append-only | SECURITY.md + history/* |
| RNF-003 | Determinismo de merge | merge gera snapshot reproduzível | `lai-pack merge` |

---

## 5 Casos de Uso (UC)

### UC-001 — Execução do thin-slice
**Atores:** usuário/serviço  
**Pré-condições:** infra local up  
**Fluxo principal:**  
1. Disparar evento/req  
2. Processar  
3. Persistir/emitir evento  
4. Confirmar resultado

**Fluxos alternativos:** retries, idempotência  
**Erros esperados:** validação, timeout, schema mismatch

### UC-002 — Correção via OCA (PackX.Y)
**Fluxo:** bug → OCA → merge → snapshot → book atualizado

---

## 6 Diagramas (placeholders)

### 6.1 Arquitetura (Mermaid)
```mermaid
flowchart LR
  user[User/Client] --> svc[{module}]
  svc --> bus[(Event Bus)]
  svc --> db[(DB)]
```

### 6.2 Sequência (Mermaid)
```mermaid
sequenceDiagram
  participant U as User/Client
  participant S as {module}
  participant B as Bus
  U->>S: request/event
  S->>B: publish/consume
  S-->>U: response/result
```

### 6.3 Classes (opcional)
Adicionar diagrama de classes apenas se ajudar manutenção.

---

## 7 Rastreabilidade

| Requisito | Contrato | Teste | Runbook | Observabilidade |
|---|---|---|---|---|
| RF-001 | contracts/* | tests/e2e/* | runbooks/HOW_TO_RUN.md | observability/* |
| RF-002 | contracts/events/* | tests/integration/* | runbooks/HOW_TO_RUN.md | observability/* |
| RNF-002 | SECURITY.md | tests/* | runbooks/HOW_TO_DEPLOY.md | history/* |

---

## 8 Plano de Implementação

### 8.1 Estratégia por packs
- Pack0: planejamento + gates
- Pack1: thin-slice executável
- Pack1.1+: correções via OCA + merge + book automático

### 8.2 Tarefas
- [ ] Definir contratos e eventos do módulo {module}
- [ ] Definir persistência mínima (se aplicável)
- [ ] Definir testes e runbooks
- [ ] Definir rollout/rollback

### 8.3 Riscos
- Drift de padrões → mitigado por DoD + validate-pack0 + book automático
- Falhas em unzip/timeouts → mitigado por snapshots pequenos + inventário

---

## 9 Testes
- Unit: regras e validações
- Integration: contratos/eventos
- E2E: thin-slice

---

## 10 Aceite
Critérios objetivos:
- comandos `make up` e `make test` passam
- validate-pack0 sem lacunas críticas

---

## 11 Rollout
Estratégia mínima:
- stage → prod
- feature flags quando necessário

---

## 12 Rollback
Plano mínimo:
- desativar feature flag (se houver)
- reverter pack para versão anterior

---

## 13 Definition of Done
Referência: `docs/DEFINITION_OF_DONE.md`

"""
    if module.strip().lower() == "meetcore":
        return base + f"""
---

## 9 MeetCore — requisitos específicos (alta complexidade)

> Este bloco é obrigatório quando `module=meetcore` porque o MeetCore é tempo-real e exige budgets de latência/escala.

### 9.1 Thin-slices (PECs) recomendados
- PEC1.01: Signaling + Rooms + Tokens (2 participantes) + eventos call.started/call.ended
- PEC1.02: Media pipeline (SFU) + ICE/TURN (simulado no início) + /health
- PEC1.03: Recorder + Storage (configurável) + transcript service (stub → real)
- PEC1.04: Insight Bus (janelas de áudio/texto) + cockpit minimal (timeline)
- PEC1.05: Post-call worker + relatório derivado + atualização de CRM simbólico

### 9.2 Budgets (SLO/SLI iniciais)
- Latência (streaming): p95 <= 300ms (meta)
- Insights: p95 <= 1s (meta)
- Transcrição parcial: p95 <= 2s (meta)
- Disponibilidade: >= 99.5% (MVP)
- Escala: 50 calls simultâneas (MVP), 200 (fase 2)

### 9.3 Contratos (CloudEvents)
Obrigatório declarar schemas para:
- meetcore.call.started / meetcore.call.ended
- meetcore.transcript.partial
- meetcore.postcall.completed

### 9.4 Segurança & privacidade (baseline)
- TLS 1.3+ em trânsito; criptografia at-rest onde aplicável
- Segregação por tenant (tenant_id em todos eventos)
- Auditoria append-only para ações administrativas
- Retenção: minimizar bruto; preferir derivados governados quando possível
"""
    return base



def _dod_template() -> str:
    return """# Definition of Done (DoD) — Pack0

Checklist mínimo para validar o Pack0 (planejamento).

- docs/PLAN.md contém: Introdução, Visão Geral, RF, RNF, UC, Diagramas, Rastreabilidade, Plano, Testes, Aceite, Rollout, Rollback, DoD
- docs/PROMPT_CONTINUIDADE.md presente
- docs/TROUBLESHOOTING.md presente
- runbooks (HOW_TO_RUN / DEPLOY / ROLLBACK) presentes
- contracts placeholder presente (contracts/README.json)

Gate objetivo:
- `lai-pack validate-pack0` deve passar (ou registrar explicitamente “não aplicável” com justificativa)

"""


def _continuity_template(module: str) -> str:
    return f"""# Prompt de Continuidade (Pack0 — {module})

Este arquivo existe para re-hidratar o GPT Builder sem depender de memória entre chats.

## Padrões imutáveis
- Pack-first: toda entrega é RELEASE PACK.
- DoD por pack: run + test + docs + manifest + audit.
- Sem camuflagem/execução velada/obfuscação de logs.

## Cadeia de packs
- Atual: pack0-{module}@0.0.1

## Próximo pack esperado
- pack1-{module}@1.0.0 (thin-slice executável)
"""

def _troubleshooting_template() -> str:
    return """# Troubleshooting (padrão)

## Sintomas comuns
- Falha ao subir compose
- Testes quebrando
- Erro de contrato/evento

## Correção padrão
- Gerar OCA-REPORT (se só diagnóstico) ou OCA-PATCH (se alterar código)
- Executar merge + testes + docs
"""

def _how_to_run_template(module: str) -> str:
    return f"""# HOW_TO_RUN — {module} (Pack0)

Este é um Pack0 de planejamento. Ele não sobe o serviço final.
Próximo passo: gerar Pack1 ({module}) com código executável.
"""

def _how_to_deploy_template(module: str) -> str:
    return f"""# HOW_TO_DEPLOY — {module}

Placeholder (Pack0). Defina deploy no Pack1.
"""

def _how_to_rollback_template(module: str) -> str:
    return f"""# HOW_TO_ROLLBACK — {module}

Placeholder (Pack0). Defina rollback no Pack1.
"""


def _meetcore_slices_template() -> str:
    return """# MEETCORE_SLICES — MeetCore-first slicing (PEC Chain)

Este documento é um artefato explícito para evitar drift e manter o MeetCore evoluindo em fatias executáveis.

## Visão
MeetCore é o módulo de maior complexidade operacional (tempo real / mídia / pós-call). Para manter previsibilidade, o módulo deve nascer fatiado.

## Slices recomendados (PEC1.01 → PEC1.05)
- PEC1.01 — Signaling + Rooms + Tokens + eventos `meetcore.call.started`/`meetcore.call.ended`
- PEC1.02 — Media pipeline (SFU) + ICE/TURN + /health + métricas básicas
- PEC1.03 — Recorder + Storage (política de retenção) + transcrição (stub→real)
- PEC1.04 — Real-time Insight Bus (janelas de áudio/texto) + Cockpit minimal (timeline)
- PEC1.05 — Post-call worker + relatório derivado + atualização de CRM simbólico

## Regra de progressão
- Cada PEC só é promovida via `merge --mode promoted` (evidência dentro do snapshot).
- O Pack1 do MeetCore deve começar pelo PEC1.01 (thin-slice).
"""


def _meetcore_budgets_template() -> str:
    return """# PERFORMANCE_BUDGETS — MeetCore (SLO/SLI iniciais)

Este documento define budgets mínimos para evitar regressão e guiar decisões de arquitetura.

## Latência (targets iniciais)
- Streaming (p95): <= 300ms
- Insights (p95): <= 1s
- Transcrição parcial (p95): <= 2s

## Escala (targets iniciais)
- MVP: 50 calls simultâneas
- Fase 2: 200 calls simultâneas (com workers paralelos)

## Observabilidade mínima
- Logs estruturados + trace_id
- Métricas de jitter/packet loss e queue lag (pós-call)
"""


def _data_retention_matrix_template() -> str:
    return """# DATA_RETENTION_MATRIX — Matriz de Retenção por Módulo (governança)

Regra: retenção por módulo é definida por risco, finalidade e governança.

## MeetCore (Sales / Calls)
- Pode armazenar gravações quando necessário (ex.: auditoria, qualidade, treinamento), sob:
  - consentimento, opt-in, e política de retenção configurável por tenant
  - criptografia at-rest + TLS em trânsito
  - trilha de auditoria append-only para acessos
- Preferir armazenar derivados governados (transcrição, eventos, relatórios) quando possível.

## Culture & People (Pipeline Efêmero)
- Pipeline efêmero: nenhum dado bruto persistido
- Persistir somente derivados governados (vetores, relatórios, evidências mínimas) com RBAC/TBAC e auditoria.

## Regras gerais
- Minimização: armazenar o mínimo necessário para finalidade declarada.
- Exclusão: suportar retenção e exclusão por tenant.
"""

def _connect_slices_template() -> str:
    return """# CONNECT_SLICES — LAI Connect (thin-slices / PEC)

Este documento define *thin-slices* para o módulo **LAI Connect** (SaaS omnichannel),
com foco em **APIs oficiais**, **opt-in**, **auditoria** e **não perda semântica** (eventos ricos).

## Objetivo
- Capturar mensagens inbound (ex.: WhatsApp via API oficial) sem perda de contexto
- Normalizar em eventos **CloudEvents** canônicos (`lai.connect.message.received`)
- Executar roteamento por regras governadas (state machine) e produzir outbound (`...message.sent`)
- Registrar auditoria append-only (`trace_id`, `tenant_id`, `actor_id`, `channel`, `consent_ref`)

## Thin-slices (PEC)
- PEC1.01 — Inbound Message → Event Bus (CloudEvents) + Idempotência
- PEC1.02 — Identity resolution (tenant-safe) + RBAC/TBAC (mínimo)
- PEC1.03 — Decision Router (regras + handoff) + Audit trail
- PEC1.04 — Outbound Sender (API oficial) + rate limits + retries
- PEC1.05 — Observabilidade: logs/métricas/traces + SLO inicial + alertas básicos

## Contratos mínimos
- `lai.connect.message.received.v1`
- `lai.connect.message.sent.v1`

## Segurança operacional
- Zero-trust + segregação por tenant
- Opt-in obrigatório para mensagens proativas
- Sem scraping / sem bypass / sem "simular humano" (somente APIs oficiais)
"""

def _app_lai_slices_template() -> str:
    return """# APP_LAI_SLICES — App LAI (thin-slices / PEC)

Este documento define *thin-slices* para o **App LAI** como hub operacional:
feed governado, rotinas e superfícies de decisão.

## Objetivo
- Consolidar eventos do ecossistema em um feed governado (`lai.app.feed.item.created`)
- Entregar UX simples (cockpit) com clareza de próximos passos e trilhas
- Integrar com GPT corporativo (RAG) de forma auditável e com minimização

## Thin-slices (PEC)
- PEC1.01 — Feed ingest (Event Bus → Feed) + dedupe + permissão por papel
- PEC1.02 — Feed read API + paginação + filtros por tenant/time
- PEC1.03 — Notificações (push/email) via canais oficiais + preferências
- PEC1.04 — GPT interno: consulta RAG + citações + policy guardrails
- PEC1.05 — Painel Master (governança): métricas e trilhas (sem exposição indevida)

## Contratos mínimos
- `lai.app.feed.item.created.v1`
- `lai.app.notification.requested.v1`

## Segurança operacional
- Privacidade por design, minimização e opt-out
- Auditoria append-only para ações administrativas
"""

def _culture_people_slices_template() -> str:
    return """# CULTURE_PEOPLE_SLICES — LAI Culture & People (thin-slices / PEC)

Pipeline focado em derivados governados (não persistir dados brutos),
com RBAC/TBAC e política de retenção/exclusão por tenant.

## Objetivo
- Processar sessões (ex.: MeetCore) e gerar **derivados governados** para cultura/desenvolvimento
- Persistir apenas: scores, tendências, eventos e relatórios mínimos (sem “dossiês”)
- Garantir opt-out, retenção configurável e exclusão sob demanda

## Thin-slices (PEC)
- PEC1.01 — Ingest de eventos (ex.: `meetcore.call.ended`) → pipeline efêmero
- PEC1.02 — Feature extraction governada (texto/voz) → vetores/scores (mínimo)
- PEC1.03 — Relatório governado (`lai.culture.session.report.created`) + evidências mínimas
- PEC1.04 — Painel para gestores (agregado) + alertas (sem exposição individual indevida)
- PEC1.05 — Controles: retenção, exclusão, opt-out, kill switch, auditoria

## Contratos mínimos
- `lai.culture.session.report.created.v1`

## Segurança operacional
- Sem diagnóstico clínico; apenas sinais observáveis e recomendações genéricas
- Efêmero por padrão; derivados governados sob controle de acesso
"""
