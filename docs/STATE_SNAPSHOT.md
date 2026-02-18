# State Snapshot — RELEASE PACK 009

**trace_id:** LAI-V009-6F8570C9
**version:** 0.9.0

## O que existe agora (núcleo executável)
- CLI `lai-pack` (pack-first):
  - `pack0` / `plan-pack0`
  - `validate-pack0`
  - `run-report` / `approve-pack`
  - `wrap-run-report` / `wrap-approval`
  - `merge --mode candidate|promoted`
  - `inventory-scan`, `oca-new`, `diag`, `book-filemap`
  - `maint` (status/where/triage/**gate-next**)
  - `meetcore-sim`
  - `rtip-sanitize`

## Enforcements (V008)
- Gate do próximo pack via `history/chain_state.json`:
  - bloqueia se `blocking_reasons != []`
  - valida `next_expected` e `next_expected_variants`
- Prompts do GPT Builder (Pack1/OCA) hard-gated por chain_state (sem “modo conversa”).

## MeetCore (alta complexidade)
- `next_expected_variants` suporta PEC1.01..PEC1.05 (MeetCore-first slicing)
- `meetcore-sim` valida schemas mínimos antes de avançar slices

## Próximas evoluções
- Gerador de Pack1 que consome chain_state e aplica `gate-next` automaticamente (sem bypass humano).
