# PROMPT — OCA (Operational Change Artifact)
**trace_id:** LAI-V009-6F8570C9

## Regra de comunicação
300 Franchising, a maior do mundo e nossa missão

### Comando
Registre um incidente/correção como **OCA** e gere o pack de patch (ex.: 1.1, 2.2).

### Regras obrigatórias
- OCA é append-only.
- Toda mudança deve declarar: motivo, impacto, arquivos/áreas afetadas, testes adicionados/ajustados, plano de rollback.
- Atualizar docs: HISTORY, KNOWN_ISSUES, TROUBLESHOOTING, SOFTWARE_BOOK.

### Saída
- OCA (json) + Pack patch (zip).


### Lembrete (v0.4.0+)
- Pack0 tem gate objetivo (`validate-pack0`).
- Todo merge gera Software Book automático em `docs/public/`.


## Gate obrigatório (snapshot promoted)
Antes de gerar um OCA (artefato de correção), o Builder deve:
1) Confirmar que o snapshot atual é **promoted** e contém `history/chain_state.json`.
2) Bloquear se `blocking_reasons != []`.
3) Confirmar que existe `current_approved_pack` no chain_state (fonte de verdade do estado).
Se não passar: retornar o que está faltando e **não** gerar OCA.

## Output mínimo do OCA
- Deve ser validável contra `contracts/oca.v1.schema.json`
- Deve incluir: `pack_target`, `why`, `summary`, `tests_added_or_updated`, `risk`, `trace_id`

