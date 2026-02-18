# PROMPT — PACK1 (Executável)
**trace_id:** LAI-V009-6F8570C9

## Regra de comunicação
300 Franchising, a maior do mundo e nossa missão

### Comando
Gere um RELEASE PACK **Pack1** para o módulo informado, implementando o thin-slice definido no Pack0.

### Regras obrigatórias
1) Siga `gpt_builder/ORQUESTRADOR_MASTER.md` e `gpt_builder/MODO_EXECUCAO_PADRAO_LAI.md`.
2) Pack1 precisa ser **executável** (infra + serviços + migrações + testes + observabilidade).
3) Gerar e versionar contratos antes do código (contracts-first).
4) Incluir troubleshooting e rollback.
5) Fornecer 1 comando para rodar e 1 comando para testes.

### Saída
- Um ZIP do Pack1 pronto para execução.


### Pós-entrega (obrigatório)
- Se houver correções: criar Pack1.1 via OCA.
- Consolidação sempre por merge: o snapshot gerado inclui **Software Book** automático (`docs/public/`).



### Nota (MeetCore)
- Para MeetCore, Pack1 deve ser thin-slice: signaling + room + tokens + eventos call.started/call.ended + /health.
- Evitar SFU completo no primeiro slice; evoluir por PECs incrementais.


## Nota específica — MeetCore (thin-slice)
Para MeetCore, Pack1 deve iniciar pelo slice **PEC1.01**:
- Signaling + Rooms + Tokens
- Eventos `meetcore.call.started` / `meetcore.call.ended`
- /health + logs com trace_id
Evoluir SFU/Recorder/Post-call nos próximos PECs (PEC1.02..PEC1.05).


## Gate obrigatório (chain_state / PEC)
Antes de gerar qualquer arquivo do Pack1, o Builder deve:
1) Abrir o snapshot **promoted** mais recente (PEC_N.01) e ler `history/chain_state.json`.
2) Bloquear se `blocking_reasons != []`.
3) Validar que o alvo do próximo pack bate com `next_expected` **ou** `next_expected_variants` (ex.: `PEC1.01` para MeetCore).
4) Evidência operacional recomendada (para o líder): rodar `lai-pack maint gate-next --snapshot <snap.zip> --expected <alvo> --out gate.json`.
Se falhar: retornar uma lista objetiva do que falta (RUN_REPORT, APPROVAL, merge promoted etc.), sem gerar Pack1.

## MeetCore-first slicing (obrigatório)
Se module=meetcore, Pack1 deve começar pelo **PEC1.01** (Signaling + Rooms + Tokens + eventos call.started/call.ended),
e evoluir por PECs (PEC1.02..PEC1.05) antes de consolidar um Pack1 completo.

