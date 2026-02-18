# Changelog

## 0.11.0
- **Team-safe default-deny (pack0_only):** `export-team-pack` agora **recusa Release Pack** como entrada e opera a partir de **snapshot promoted** (PEC Chain).
- **No-leak gate hard:** novo comando `leak-check` gera `leak_report.json` e falha (exit code != 0) se detectar qualquer violação da policy.
- **Contrato de audiência:** nova policy declarativa `governance/audience_policy.team_pack0_only.v1.json` (allowlist + denylist + regex).
- **Sem placeholders proibidos:** `docs/references/` e `02_INVENTORY/semantic_index/` não são criados no Team Pack (evita drift / falso-positivo e simplifica auditoria).
- **Release Pack limpo:** removidos `.pytest_cache/`, `__pycache__/` e `*.pyc` do pacote final.
- **Runbook Comando-Mestre:** `runbooks/EXECUTAR_FABRICA_TEAM_SAFE_V011.sh` (Pack0 → Gates → Snapshot → Export → Leak-check).

## 0.10.1
- Fix crítico: `plan-pack0` agora gera slices para `lai-connect`, `app-lai` e `culture-people` (sem NameError) + testes E2E cobrindo os 4 módulos.
- ONCA: `onca-validate` agora trata `duplicate_sha256` como **warning** (não bloqueia); bloqueios continuam para `duplicate_onca_id`, `duplicate_path` e `parse_errors`.
- Manual operacional atualizado (catálogo completo de comandos + workflows + segurança team-safe).

## 0.10.0
- Correção crítica de exposição: `docs/references/` e `02_INVENTORY/semantic_index/` foram **externalizados** (placeholders + ledger em `docs/references/EXTERNAL_INPUTS.md`).
- Policy pública: `governance/public_export_policy.json` aplicada em `docs/public/FILEMAP.md` e `docs/public/SOFTWARE_BOOK.md` (gerados em merge).
- Export seguro: novos comandos `export-manual` (somente arquivo) e `export-team-pack` (ZIP filtrado team-safe).
- ONCA: comandos `onca-scan` e `onca-validate` (inventário auditável).
- Resolver: comando `resolve` para `zip::...::file` (zip-chains).
- Sims: `connect-sim`, `app-sim`, `culture-people-sim` (schemas mínimos).
- Pack1: `plan-pack1` / `pack1` (scaffold executável minimal).
- Book-filemap: `--include-restricted` opcional (default = public-only).

## 0.9.0
- Planner Pack0 multi-módulo: templates de slicing para **meetcore**, **lai-connect**, **app-lai**, **culture-people** (com `DATA_RETENTION_MATRIX` sempre presente).
- Validador Pack0 multi-módulo: exige `CONNECT_SLICES` / `APP_LAI_SLICES` / `CULTURE_PEOPLE_SLICES` quando aplicável + `DATA_RETENTION_MATRIX` como baseline.
- Blueprints do ecossistema incluídos em `docs/references/` (Connect/App/Culture/MeetCore) + dicionário v2.0.
- `governance/policy_flags.json`: default-deny (reference_only) para materiais legados sensíveis (rastreabilidade sem execução).
- `docs/references/EXTERNAL_INPUTS.md`: rastreabilidade de ZIPs externos por sha256.
- Atualização de trace_id, versão e documentação (RELEASE PACK 009).

## 0.4.0
- **DoD formalizado**: `docs/DEFINITION_OF_DONE.md` + Pack0 agora gera `docs/DEFINITION_OF_DONE.md` automaticamente.
- **Conformidade automática**: novo comando `lai-pack validate-pack0` (gate objetivo) com relatório de lacunas.
- **Software Book automático no merge**: `lai-pack merge` agora gera `docs/public/SOFTWARE_BOOK.md` + `docs/public/FILEMAP.md` no snapshot.
- Alias `lai-pack pack0` (compatibilidade com comando do orquestrador).

## 0.3.0
- Integração do **MEPLAI** (Modo Execução Padrão LAI) no orquestrador.
- Inclusão de referência normativa de **Documento de Requisitos** (produto).
- Prompts Pack0/Pack1/OCA atualizados para usar MEPLAI.

## 0.2.0
- Pack Factory Core (plan-pack0, merge, diag)

## 0.6.0
- PEC gating completo: RUN_REPORT + APPROVAL em patch packs append-only
- merge --mode promoted (trava sem approval)
- maint console (status/where/triage)
- meetcore-sim + schemas mínimos
- RTIP/LT100R sanitizados + assets de navegação em docs/public
- CI gate real (sem green falso)

## 0.7.0
- Gate MeetCore no Pack0: exige `MEETCORE_SLICES`, `PERFORMANCE_BUDGETS`, `DATA_RETENTION_MATRIX`.
- Orquestrador GPT Builder: gate por `history/chain_state.json` e `blocking_reasons`.
- Runbook por papel (Lucas/João/Breno).
## 0.8.0
- Gate operacional novo: `lai-pack maint gate-next` (valida chain_state.next_expected/variants e blocking_reasons)
- Prompts hard-gated: PROMPT_PACK1 e PROMPT_OCA agora exigem chain_state e bloqueiam se necessário
- next_expected robusto: suporta packN(.x.y) e pecN(.x.y) e incrementa major
- MeetCore variants: next_expected_variants PEC1.01..PEC1.05 quando aplicável
- Testes e2e adicionados para cobrir o gate-next

