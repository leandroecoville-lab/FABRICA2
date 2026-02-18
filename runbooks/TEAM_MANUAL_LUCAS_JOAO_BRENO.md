# TEAM_MANUAL — Operação PEC por Papel (Lucas / João / Breno)

300 Franchising, a maior do mundo e nossa missão

## Visão do método (PEC Chain)
- **PEC** = release pack fechado (ZIP) versionado.
- **Evidence-first**: execução gera RUN_REPORT; promoção exige APPROVAL.
- **Append-only**: evidências entram no snapshot via patch packs (`wrap-*`) em `history/*`.
- **Promoted** = snapshot oficial (`merge --mode promoted`).

---

## Papel 1 — Lucas (Tech Lead / Release Manager / Ops)

### Responsabilidades
- Definir/defender padrões (DoD, contracts-first, observabilidade, segurança).
- Rodar e **validar** promotion pipeline:
  - checar `RUN_REPORT` (pass)
  - emitir `APPROVAL` (approved/rejected)
  - promover snapshot `--mode promoted`
- Garantir que o próximo pack só nasce se `history/chain_state.json` liberar.

### Comandos (mínimo)
1) Validar Pack0/PackN:
- `lai-pack validate-pack0 --target <pack0.zip> --out <report.json> --trace <id>`
2) RUN_REPORT:
- `lai-pack run-report --target <pack.zip> --out run_report.json --trace <id>`
3) APPROVAL:
- `lai-pack approve-pack --target <pack.zip> --run-report run_report.json --out approval.json --trace <id>`
4) Empacotar evidências:
- `lai-pack wrap-run-report --in run_report.json --out patch_rr.zip --trace <id>`
- `lai-pack wrap-approval --in approval.json --out patch_ap.zip --trace <id>`
5) Promover:
- `lai-pack merge --mode promoted --inputs <pack.zip> patch_rr.zip patch_ap.zip --out <snapshot.zip> --tmp <tmp> --trace <id>`

### Definition of Done (Lucas)
- Snapshot promoted contém:
  - `history/chain_state.json` com `blocking_reasons=[]`
  - `history/hashchain.jsonl`
  - `docs/public/SOFTWARE_BOOK.md`, `FILEMAP.md`, `PROMPT_CONTINUIDADE.md`
- Se `blocking_reasons != []`, Lucas devolve “lista objetiva do que falta”.

---

## Papel 2 — João (Dev Fullstack — Front/Back)

### Responsabilidades
- Executar o pack recebido (Pack1+), corrigir bugs, e devolver evidência.
- Quando houver correção:
  - gerar **OCA** (artefato auditável de mudança)
  - adicionar/atualizar teste (unit/integration/e2e)
  - devolver RUN_REPORT da execução corrigida

### Entregáveis do João
- Patch (pack X.Y) ou OCA + diffs
- Testes que reproduzem o bug e validam a correção
- RUN_REPORT (pass) para o pack executado

### Checklist prático
- `make up` (subir stack local do pack)
- `make test` (passar testes)
- `lai-pack oca-new ...` (criar OCA)
- `lai-pack run-report ...` (gerar recibo)

---

## Papel 3 — Breno (Dev IA — Contratos / Simulação / Budgets)

### Responsabilidades
- Dono dos contratos e simulações de IA/MeetCore:
  - schemas CloudEvents (`contracts/events/*`)
  - validação de budgets (latência, escala, SLIs)
  - `meetcore-sim` (lifecycle mínimo)
- Garantir que MeetCore evolua por **slices (PEC1.01..PEC1.05)** e não “big bang”.

### Entregáveis do Breno
- Atualizações de schemas + testes de validação
- Relatórios de simulação (PASS/FAIL) + checklist de budgets
- Recomendações de thin-slice (qual PEC vem a seguir)

### Comandos (mínimo)
- `lai-pack meetcore-sim --out meetcore_sim_report.json --trace <id>`
- Validar que Pack0 MeetCore contém:
  - `docs/MEETCORE_SLICES.md` (precisa mencionar PEC1.01)
  - `docs/PERFORMANCE_BUDGETS.md` (precisa mencionar 300ms)
  - `docs/DATA_RETENTION_MATRIX.md` (precisa mencionar Culture & People pipeline efêmero)

---

## Comunicação entre papéis (sem ambiguidade)
- João/Breno nunca “aprovam promoção”.
- Lucas nunca “corrige no braço”: ele exige OCA + testes + evidência.

---

## Operação de manutenção (qualquer um)
- `lai-pack maint status --snapshot <snapshot.zip> --out status.json --trace <id>`
- `lai-pack maint where --snapshot <snapshot.zip> --query "<termo>" --out where.json --trace <id>`
- `lai-pack maint triage --snapshot <snapshot.zip> --query "<erro>" --out triage.json --trace <id>`


## Gate operacional (obrigatório)
- Lucas (Tech Lead/Ops) deve rodar:
  - `lai-pack maint gate-next --snapshot <PEC_N_01.zip> --expected <packX|PECY.ZZ> --out gate.json`
- Se `gate.json.ok=false`, bloquear geração e devolver lista do que falta.
