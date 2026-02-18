# ENGINEERING_MANUAL — Operação da Fábrica PEC (v0.10.0)

## TL;DR (papéis)
- **Dev/Time**: executa pack, gera RUN_REPORT, propõe OCA quando necessário.
- **Líder**: aprova (APPROVAL) e promove snapshot via merge `--mode promoted`.
- **Fábrica**: gera documentação automática + estado (chain_state) + ledger (hashchain).

## Regras duras
1) Nada de código solto: tudo é ZIP (pack, patch pack, snapshot).
2) Patch pack é append-only em `history/*`.
3) `merge --mode promoted` bloqueia sem approval aprovado.
4) Toda execução gera RUN_REPORT; toda promoção gera APPROVAL.

## Nomenclatura
- PEC = pack/snapshot versionado na cadeia (ex.: PEC0.01, PEC1.02)
- Candidate = merge sem promoção (modo candidate)
- Promoted = merge com promoção (modo promoted)

## Fluxo padrão (MeetCore)
1) Gerar Pack0 (planejamento):
   - `pack0 --module meetcore`
2) Gate de qualidade:
   - `validate-pack0`
3) Execução do time:
   - rodar o pack (quando for Pack1+) e gerar RUN_REPORT
4) Aprovação do líder:
   - `approve-pack`
5) Empacotar evidências:
   - `wrap-run-report`, `wrap-approval`
6) Promover snapshot:
   - `merge --mode promoted`

## Como abrir o estado do sistema
- `maint status --snapshot <zip>` → retorna `chain_state` e contagens.
- `docs/public/PROMPT_CONTINUIDADE.md` → “o que fazer agora”
- `docs/public/SOFTWARE_BOOK.md` → visão operacional do snapshot
- `docs/public/FILEMAP.md` → lista de arquivos/pastas

## Troubleshooting (MeetCore)
- Se falhar ICE/TURN: checar runbooks + triage “ICE failed”
- Se latência subir: verificar budgets no Pack0 MeetCore e logs/traces
- Se event schema falhar: corrigir contracts-first e regenerar pack patch

## Controles de governança (mínimo)
- tenant_id em todos eventos
- audit append-only (history/hashchain.jsonl)
- sem obfuscação/execução velada


## Manual por papel (time)
Ver: `runbooks/TEAM_MANUAL_LUCAS_JOAO_BRENO.md`.


## Gate operacional (obrigatório)
- Sempre rodar `lai-pack maint gate-next` antes de gerar o próximo pack.
- Se retornar exit code 2: corrigir bloqueios (RUN_REPORT/APPROVAL/merge promoted) e só então avançar.
