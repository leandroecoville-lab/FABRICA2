# Mapa Mestre Auditável do Ecossistema LAI (v0.1)

**Gerado em (UTC):** 2026-01-18T20:39:34Z  
**Objetivo:** transformar o inventário RTIP/LT-100R em um **mapa único, coerente e auditável**, servindo como base do **Planejamento Mestre do Ecossistema** e, em seguida, como base de geração de **Pack0 individuais** (Connect / MeetCore / App / Culture & People) **sem inconsistência**.

---

## 1) Fonte de verdade (arquivos) + Hierarquia

### 1.1 Arquivos-chave (ponteiros auditáveis)
- **Blueprint LAI Connect** → `/mnt/data/Lai Connect - blueprint confidencial.pdf`
- **Addon Connect Text Insights (zip)** → `/mnt/data/7pacote de dados connect leitura intencao texto.zip`
- **Blueprint App LAI** → `/mnt/data/App lai blueprint - confidencial.pdf`
- **Doc MeetCore (25.pdf)** → `/mnt/data/25.pdf`
- **Blueprint Culture & People** → `/mnt/data/Lai Culture & People documentac╠ºa╠âo te╠ücnica.pdf`
- **Dicionário (Reinterpretação Big Tech)** → `/mnt/data/LAI — REINTERPRETAÇÃO BIG TECH v1.0 .pdf`
- **VS4 Investigação Universal** → `/mnt/data/Vs4 Comando investigação universal (1).pdf`
- **VS2 Integração Universal** → `/mnt/data/Vs2 Comando integração universal.pdf`
- **Resumo App LAI** → `/mnt/data/App Lai - sistema Lai resumo.pdf`
- **4 Pilares e Gatilhos** → `/mnt/data/Lai - 4 pilares e gatilhos.pdf`
- **Planejamento LAI Connect (PDF)** → `/mnt/data/planejamento lai conect.pdf`
- **Planilha (Dev do zero)** → `/mnt/data/planilha desenvolvimento de software do zero .pdf`
- **Catálogo RTIP Enriquecido v0.2** → `/mnt/data/Catalogo_RTIP_enriched_v0.2.xlsx`
- **Índice Navegável v0.2** → `/mnt/data/Indice_Navegavel_v0.2.md`
- **Ledger LT-100R v0.2** → `/mnt/data/LT100R_FASE4_LeituraLedger_v0.2.xlsx`

### 1.2 Regra de hierarquia (quando houver conflito)
1) **Blueprints oficiais** (Connect / App / MeetCore / Culture & People)  
2) **Segurança & Governança** (políticas, RBAC/TBAC, auditoria)  
3) **Planilhas estruturais** (métricas, scores, estruturas de sinais observáveis)  
4) **Estudos/Referências**  
5) **Legado/Hipótese** (não apagado; apenas marcado)

> Nota de governança: conteúdos que sugerem “influência arquitetônica de fluxo (nunca da pessoa)”, “perfilamento sensível não governado” ou “evasão de governança” são tratados como **Risco de Compliance** e **não viram requisito funcional automático**. Eles podem virar **lições de UX/treino com transparência e opt-in**, ou ficar como “legado”.

---

## 2) Propósito total do software (north-star)

### 2.1 O ecossistema LAI resolve
- **Operação omnichannel** com captura sem perda semântica (conversas + contexto + outcomes).
- **Unificação de identidade** (pessoa/conta) cross-canais com governança.
- **Motor de recomendação operacional** (“next best action”) baseado em sinais contextuais (texto) e sinais observáveis (MeetCore), sempre com auditoria.
- **Ciclo fechado de melhoria**: logs → métricas → templates/prompts → melhoria contínua (com rollback e trilha de auditoria).

### 2.2 Produtos/módulos (Pack0-alvo)
- **LAI Connect**: SaaS omnichannel (WhatsApp/DM/e-mail/CRM) + roteamento + automação governada.
- **MeetCore**: motor de videoconferência + artefatos pós-call + stream de sinais observáveis (não clínicos).
- **App LAI**: cockpit corporativo (tarefas, dashboards, playbooks, trilhas de execução).
- **Culture & People**: pipeline de pessoas/cultura com processamento efêmero + vetorização governada + relatórios agregados.

---

## 3) OCA — Inventário Semântico (domínios de dados)

- **OCA.IDENTITY** — Tenant, usuários, papéis, RBAC/TBAC, sessão, consentimentos.
- **OCA.CHANNEL** — Canais (WhatsApp/DM/e-mail/voz), conectores oficiais, opt-in, rate limit.
- **OCA.CONVERSATION** — Threads, participantes, estados de funil, contexto de conta.
- **OCA.MESSAGE** — Mensagens inbound/outbound, anexos, normalização, idempotência.
- **OCA.CRM** — Leads/deals/stages, sincronização com HubSpot/CRM, ownership e SLA.
- **OCA.TEXT_INSIGHTS** — Leitura de camadas contextuais (texto): intenção, sinais, recomendação, auditoria de evidências.
- **OCA.MEETING** — Sessão MeetCore: participantes, timeline, artefatos (transcrição/sumário), eventos.
- **OCA.OBSERVABLE_SIGNALS** — Sinais não verbais permitidos (observáveis e não clínicos): gaze/blink/turn-taking/pausas; sempre governado.
- **OCA.SCORES** — Scores operacionais e de qualidade (não clínicos): performance, cadência, follow-up, compliance, saúde de funil.
- **OCA.AUDIT** — Auditoria append-only: ações administrativas, mudanças de configuração, envio de mensagens, acessos.
- **OCA.EXPERIMENTS** — Feature flags, A/B, versões de templates/prompts, rollouts e kill-switch.

**Regra de ouro OCA:** todo dado bruto sensível deve ser minimizado; preferir **derivados agregados** e **pointers** auditáveis. Biometria/sinais visuais só entram sob opt-in, retenção mínima e kill-switch.

---

## 4) Arquitetura canônica (Big Tech frugal)

### 4.1 Princípios
- **Event Bus** como espinha dorsal.
- Serviços orientados a eventos com **idempotência** e **replay**.
- **Multi-tenant** com segregação por `tenant_id`.
- **RBAC/TBAC** e auditoria append-only.
- Thin-slice end-to-end antes de expandir.

### 4.2 Serviços mínimos (visão de ecossistema)
- `gateway-api` (AuthN/AuthZ, rate limit, tenant routing)
- `event-bus` (Kafka/NATS/SQS+SNS — escolha por custo)
- `connect-webhook-service` (WhatsApp/CRM webhooks → normalização)
- `connect-router-service` (regras de funil + handoffs)
- `connect-text-insights-service` (módulo Leitura Escrita — serviço isolado)
- `meetcore-call-service` (sessões + eventos)
- `meetcore-postcall-workers` (transcrição/sumário/sinais observáveis)
- `culture-people-core` (transições + relatórios agregados)
- `app-lai-frontend` + `app-lai-api` (cockpit)
- `audit-log-service` (append-only; trilhas e consultas)

---

## 5) Diagrama textual de fluxo (eventos)

### 5.1 Thin-slice mínimo (Connect → Text Insights → CRM → App)
1) **Webhook inbound** chega (WhatsApp/DM/CRM) → `connect-webhook-service`  
2) Normaliza e persiste `Message`/`Conversation` → publica `lai.connect.message.received`  
3) `connect-router-service` decide:  
   - chama `connect-text-insights-service` (`/v1/text-insights/analyze`)  
   - recebe `{intent, confidence, recommendation, audit}`  
4) Publica `lai.connect.text_insights.generated`  
5) Atualiza CRM (`lai.connect.crm.lead.upserted`) e gera task no App  
6) Operador vê recomendação + auditoria (evidence/confidence) e executa

### 5.2 MeetCore → Culture & People → App (loop)
1) `lai.meetcore.call.ended` → workers geram transcript/sumário  
2) Publica `lai.meetcore.transcript.ready` + sinais observáveis governados  
3) `culture-people-core` calcula scores agregados → `lai.culture.score.updated`  
4) `app-lai` atualiza dashboards e playbooks

---

## 6) Contratos (eventos + APIs)

### 6.1 Eventos canônicos (nomes)
- `lai.connect.webhook.received` — Entrada bruta de webhook (WhatsApp/CRM).
- `lai.connect.message.received` — Mensagem inbound normalizada + contexto mínimo.
- `lai.connect.message.sent` — Mensagem outbound enviada (com status e provider_id).
- `lai.connect.text_insights.requested` — Solicitação de análise de conversa (texto) para o serviço de insights.
- `lai.connect.text_insights.generated` — Resultado: intenção + sinais + recomendação + auditoria.
- `lai.connect.crm.lead.upserted` — Lead criado/atualizado no CRM + owner + estágio.
- `lai.connect.routing.stage.changed` — Mudança de estágio por regras de roteamento.
- `lai.meetcore.call.started` — Sessão de chamada iniciada (MeetCore).
- `lai.meetcore.call.ended` — Chamada encerrada + metadados.
- `lai.meetcore.transcript.ready` — Transcrição disponível + ponteiro para storage.
- `lai.culture.score.updated` — Score operacional/cultural atualizado (agregado, governado).
- `lai.audit.log.appended` — Registro de auditoria append-only (imutável).

### 6.2 Contrato REST mínimo (Connect Text Insights)
Fonte: pacote Connect Text Insights (OpenAPI).  
- `POST /v1/text-insights/analyze`
- `POST /v1/text-insights/baselines/{participant_id}/update`
- `GET /health`
- `GET /version`
- `GET /metrics` (Prometheus)

**Governança do contrato:** `audit.evidence_quality`, `intent.confidence` e `data_sufficiency` são obrigatórios para decidir se a recomendação pode virar automação.

---

## 7) Storage mínimo (Padrão Pack0)

### 7.1 Postgres (tabelas mínimas)
- `tenants`, `users`, `roles`, `permissions`, `sessions`
- `channels`, `channel_accounts`
- `contacts`, `accounts`
- `conversations`, `participants`, `messages`
- `crm_leads`, `crm_deals`, `crm_events`
- `text_insights_results` (resultado + auditoria; sem conteúdo excessivo)
- `meetings`, `meeting_artifacts` (pointers para storage)
- `scores` (agregado)
- `audit_log` (append-only)

### 7.2 Redis (mínimo)
- idempotency keys (webhooks)
- rate limit por canal/tenant
- cache curto de roteamento/templates

### 7.3 Object storage (S3 compatível)
- anexos (WhatsApp)
- transcript, summaries, exports governados

---

## 8) Observabilidade e auditoria (obrigatório)

- `trace_id` em todos os serviços
- Logs estruturados (JSON) + métricas + traces
- `audit_log` append-only para:
  - envio de mensagens
  - mudanças em templates/prompts
  - mudanças em regras de roteamento
  - acessos admin
- SLOs iniciais:
  - p95 analyze < 800ms (MVP)
  - erro 5xx < 0.5%
  - filas sem backlog > X minutos

---

## 9) Riscos, guardrails e decisões

### 9.1 Riscos principais
- APIs externas (WhatsApp/DM/CRM): variação de payload, rate limit, webhooks duplicados
- Multi-tenancy: vazamento cross-tenant por erro de query/ACL
- Conteúdo sensível: tentativas de “perfilamento sensível não governado” (ex.: atributos comportamentais sensíveis (alto risco)) sem opt-in e sem propósito claro
- Drift de templates/prompts sem versionamento

### 9.2 Decisões recomendadas (para manter coerência)
1) **RTIP/LT-100R como camada única de inventário** (vpaths e hashes)  
2) **Contratos primeiro**: eventos + OpenAPI → depois implementação  
3) **Observabilidade e auditoria desde o Pack0**  
4) **Sinais não verbais apenas observáveis e não clínicos**, com minimização e opt-in  
5) **Versionamento de templates/prompts** com rollback e audit log

---

## 10) Próximos passos (para virar Planejamento Mestre)

1) Congelar este mapa como “Base v0.1”  
2) Executar “Lote 3: Código/Contratos” (RTIP) para:
   - extrair eventos/endpoints reais de cada módulo
   - gerar o **Mapa de Contratos do Ecossistema** (Pack0-ready)
3) Planejamento mestre em fases:
   - Fase 1: Thin-slice Connect (WhatsApp) + Text Insights + CRM + App  
   - Fase 2: MeetCore + pós-call + follow-up no Connect  
   - Fase 3: Culture & People (agregação) + dashboards no App  

---

## Anexo A — Onde está cada coisa (guia rápido)

- Inventário mestre (hashes/vpaths): `LT100R_FASE4_LeituraLedger_v0.2.xlsx`
- Catálogo (semântica + uso): `Catalogo_RTIP_enriched_v0.2.xlsx`
- Índice navegável: `Indice_Navegavel_v0.2.md`
- Addon Connect Text Insights: `/mnt/data/7pacote de dados connect leitura intencao texto.zip`

