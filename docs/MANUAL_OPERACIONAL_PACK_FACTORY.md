# MANUAL OPERACIONAL — LAI Pack Factory (RELEASE PACK 011)

> **Objetivo operacional:** operar a fábrica em modo **pack-first**, com **gates**, **audit trail** e **exportação team-safe** (sem exposição acidental de conteúdos externalizados).

---

## OBJETIVO

1) Gerar **Pack0** (planejamento padronizado) por módulo, com rastreabilidade SRS (RF/RNF/UC) e gates automáticos.  
2) Gerar **Pack1** (scaffold executável minimal) para thin-slice.  
3) Executar a **PEC Chain** (run-report → approval → patch packs → merge promoted).  
4) Produzir **inventário auditável** do acervo (ONCA) e **resolver de zip-chains**.  
5) Garantir operação **team-safe** por padrão (sem vazamentos).

---

## REGRAS DE SEGURANÇA OPERACIONAL

### Regras “team-safe” (obrigatórias)
1) **NUNCA** compartilhe o Release Pack completo com o time.
2) Para compartilhar com o time, use **somente**:
   - `export-manual` (manual isolado, somente arquivo), e/ou
   - `export-team-pack` (ZIP filtrado, team-safe) **a partir de snapshot promoted** (PEC Chain). O comando **recusa Release Pack** por padrão (default-deny).
3) Conteúdos externalizados (ex.: `docs/references/` e `02_INVENTORY/semantic_index/`) **não devem circular** em ZIPs de time.
4) `book-filemap --include-restricted` existe, mas é **uso controlado** (pode expor inventário completo).

### Identidade / Auditoria
- Preferir executar com:
  - `LAI_ACTOR_ID=<id>` (quem rodou)
  - `--trace <TRACE_ID>` (rastreio fim-a-fim)

---

## COMO RODAR LOCAL (DEV)

```bash
# Dentro do diretório do Release Pack
PYTHONPATH=services/pack-factory python -m pytest -q
```

---

## COMANDOS (CATÁLOGO COMPLETO)

### Pack0 (Planejamento)
```bash
# gerar
PYTHONPATH=services/pack-factory python -m app.cli plan-pack0 --module meetcore --out _out --trace T0
PYTHONPATH=services/pack-factory python -m app.cli plan-pack0 --module lai-connect --out _out --trace T0C
PYTHONPATH=services/pack-factory python -m app.cli plan-pack0 --module app-lai --out _out --trace T0A
PYTHONPATH=services/pack-factory python -m app.cli plan-pack0 --module culture-people --out _out --trace T0P

# alias
PYTHONPATH=services/pack-factory python -m app.cli pack0 --module meetcore --out _out --trace T0
```

### Gate Pack0 (Validador)
```bash
PYTHONPATH=services/pack-factory python -m app.cli validate-pack0 --target _out/pack0-meetcore-0.0.1.zip --out _out/validate_meetcore.json --trace T1
```

### Merge (snapshot)
```bash
PYTHONPATH=services/pack-factory python -m app.cli merge --inputs <PACK1.zip> <PATCH_A.zip> <PATCH_B.zip> --out _out/snapshot.zip --tmp _tmp --trace T2
```

### Diagnóstico (diag)
```bash
PYTHONPATH=services/pack-factory python -m app.cli diag --target <PACK.zip> --out _out/diag.json --trace D1
```

### Inventário machine (zip)
```bash
PYTHONPATH=services/pack-factory python -m app.cli inventory-scan --target <PACK.zip> --out _out/inventory.json --trace I1
```

### OCA (contrato auditável de mudança)
```bash
PYTHONPATH=services/pack-factory python -m app.cli oca-new --kind feature --title "título" --out _out/oca.json --trace OCA1
```

### PEC Chain (promoted)
```bash
# 1) run-report (evidência)
PYTHONPATH=services/pack-factory python -m app.cli run-report --target <PACK.zip> --out _out/run_report.json --actor "$LAI_ACTOR_ID" --trace RR1

# 2) approve-pack (aprovação governada)
PYTHONPATH=services/pack-factory python -m app.cli approve-pack --target <PACK.zip> --run-report _out/run_report.json --out _out/approval.json --actor "$LAI_ACTOR_ID" --trace AP1

# 3) wrap patches (vira packs de patch)
PYTHONPATH=services/pack-factory python -m app.cli wrap-run-report --in _out/run_report.json --out _out/patch_run_report.zip --trace WR1
PYTHONPATH=services/pack-factory python -m app.cli wrap-approval --in _out/approval.json --out _out/patch_approval.zip --trace WA1

# 4) merge promoted (gera snapshot promovido)
PYTHONPATH=services/pack-factory python -m app.cli merge --mode promoted --inputs <PACK.zip> _out/patch_run_report.zip _out/patch_approval.zip --out _out/snapshot_promoted.zip --tmp _tmp --trace MPR1

# 5) gate-next (verifica próximo estágio esperado)
PYTHONPATH=services/pack-factory python -m app.cli maint gate-next --snapshot _out/snapshot_promoted.zip --expected pack1 --out _out/gate_next.json --trace GN1
```

### Maint (status/where/triage)
```bash
PYTHONPATH=services/pack-factory python -m app.cli maint status --snapshot <snapshot.zip> --out _out/status.json --trace MS1
PYTHONPATH=services/pack-factory python -m app.cli maint where --snapshot <snapshot.zip> --query "texto" --out _out/where.json --trace MW1
PYTHONPATH=services/pack-factory python -m app.cli maint triage --snapshot <snapshot.zip> --query "erro" --out _out/triage.json --trace MT1
```

### Simulações (mínimo, com validação de schema quando existir)
```bash
PYTHONPATH=services/pack-factory python -m app.cli meetcore-sim --out _out/meetcore_sim.json --trace S1
PYTHONPATH=services/pack-factory python -m app.cli connect-sim --out _out/connect_sim.json --trace S2
PYTHONPATH=services/pack-factory python -m app.cli app-sim --out _out/app_sim.json --trace S3
PYTHONPATH=services/pack-factory python -m app.cli culture-people-sim --out _out/culture_people_sim.json --trace S4
```

### Export seguro (para time)
```bash
# manual isolado (somente arquivo .md)
PYTHONPATH=services/pack-factory python -m app.cli export-manual --out _out/MANUAL_OPERACIONAL.md --trace E1

# zip team-safe (filtrado)
PYTHONPATH=services/pack-factory python -m app.cli export-team-pack --in <SNAPSHOT_PROMOTED.zip> --out _out/team_pack0_<module>.zip --trace E2

# gate hard no_leak (antes de entregar ao time)
PYTHONPATH=services/pack-factory python -m app.cli leak-check --target _out/team_pack0_<module>.zip --out _out/leak_report_<module>.json --trace E3
```

### ONCA (inventário auditável)
```bash
# scan rápido (somente top-level)
PYTHONPATH=services/pack-factory python -m app.cli onca-scan --root /mnt/data --out _out/onca.jsonl --trace ON1

# scan completo (recursivo)
PYTHONPATH=services/pack-factory python -m app.cli onca-scan --root /mnt/data --recursive --max-files 5000 --out _out/onca_recursive.jsonl --trace ON2

# validate
PYTHONPATH=services/pack-factory python -m app.cli onca-validate --in _out/onca_recursive.jsonl --out _out/onca_report.json --trace ON3
```

**Nota:** duplicidade de `sha256` é reportada como **warning** (não bloqueia), pois costuma indicar cópias/duplicação no acervo.  
Bloqueios reais: `parse_errors`, `duplicate_onca_id`, `duplicate_path`.

### Resolver zip-chains
```bash
PYTHONPATH=services/pack-factory python -m app.cli resolve --ref "zip::/mnt/data/A.zip::B.zip::docs/PLAN.md" --out _out/extracted.bin --trace R1
```

### Pack1 (scaffold executável)
```bash
PYTHONPATH=services/pack-factory python -m app.cli plan-pack1 --module meetcore --out _out --trace P1
# alias
PYTHONPATH=services/pack-factory python -m app.cli pack1 --module meetcore --out _out --trace P1
```

### Book / FileMap
```bash
# padrão: public-only (recomendado)
PYTHONPATH=services/pack-factory python -m app.cli book-filemap --target <PACK.zip> --out _out/FILEMAP.md --trace B1

# uso controlado: inclui paths restritos (pode expor inventário completo)
PYTHONPATH=services/pack-factory python -m app.cli book-filemap --target <PACK.zip> --out _out/FILEMAP_ALL.md --include-restricted --trace B2
```

---

## WORKFLOWS RECOMENDADOS

### 1) “Clone Engenheiro” — rotina segura
1) Gere Pack0 do módulo alvo.
2) Rode `validate-pack0`.
3) Gere Pack1 (quando entrar em execução).
4) Rode simulação do módulo.
5) Gere snapshot via `merge`.
6) Antes de compartilhar: `export-team-pack`.

---

## O QUE FOI PEDIDO / O QUE FOI OMITIDO / O QUE DEVERIA TER SIDO PEDIDO

- **Pedido:** operar com segurança (sem vazamento) + V010 coerente/testado → entregue via export team-safe + policy + gates + simulações.
- **Omitido:** conteúdos externalizados não circulam no pack; são rastreados por sha256 (ledger) e consumidos via `resolve`.
- **Deveria ter sido pedido:** matriz de visibilidade por papel (dev/ops/líder) para refinar ainda mais o export team-safe.
