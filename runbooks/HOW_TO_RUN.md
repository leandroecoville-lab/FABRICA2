# HOW_TO_RUN — LAI Pack Factory (v0.10.0)

## Rodar (1 comando)
```bash
make up
```

## Rodar testes (1 comando)
```bash
make test
```

## Fluxo PEC (Pack0 -> RUN_REPORT -> APPROVAL -> PATCH -> MERGE PROMOTED)

### 1) Gerar Pack0 (planejamento)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   pack0 --module meetcore --out /data/out --trace T0
```

### 2) Validar Pack0 (gate objetivo)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   validate-pack0 --target /data/out/pack0-meetcore-0.0.1.zip --out /data/out/pack0_validation.json --trace T0
```

### 3) Gerar RUN_REPORT (recibo)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   run-report --target /data/out/pack0-meetcore-0.0.1.zip --out /data/out/run_report.json --trace T1
```

### 4) Gerar APPROVAL (líder)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   approve-pack --target /data/out/pack0-meetcore-0.0.1.zip --run-report /data/out/run_report.json --out /data/out/approval.json --trace T2
```

### 5) Empacotar RUN_REPORT/APPROVAL como patch packs append-only
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   wrap-run-report --in /data/out/run_report.json --out /data/out/patch_rr.zip --trace T3

docker compose -f infra/docker-compose.yml run --rm pack-factory   wrap-approval --in /data/out/approval.json --out /data/out/patch_ap.zip --trace T4
```

### 6) Merge promoted (gera snapshot PEC0.01)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   merge --mode promoted --inputs /data/out/pack0-meetcore-0.0.1.zip /data/out/patch_rr.zip /data/out/patch_ap.zip   --out /data/out/PEC0_01_snapshot.zip --tmp /data/tmp --trace T5
```

## Console de manutenção (snapshot)
### status
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   maint status --snapshot /data/out/PEC0_01_snapshot.zip --out /data/out/maint_status.json --trace T6
```

### where
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   maint where --snapshot /data/out/PEC0_01_snapshot.zip --query "meetcore" --out /data/out/where.json --trace T7
```

### triage
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   maint triage --snapshot /data/out/PEC0_01_snapshot.zip --query "ICE failed" --out /data/out/triage.json --trace T8
```

## Simulação MeetCore (mínimo)
```bash
docker compose -f infra/docker-compose.yml run --rm pack-factory   meetcore-sim --out /data/out/meetcore_sim_report.json --trace T9
```


## Gate MeetCore (Pack0)
Para `module=meetcore`, o Pack0 deve conter:
- docs/MEETCORE_SLICES.md
- docs/PERFORMANCE_BUDGETS.md
- docs/DATA_RETENTION_MATRIX.md
O validator falha se faltar.

## Export seguro (team-safe)
Nunca distribua o Release Pack completo para o time. Use:

```bash
PYTHONPATH=services/pack-factory python -m app.cli export-manual --out _out/MANUAL.md --trace E1
PYTHONPATH=services/pack-factory python -m app.cli export-team-pack --in LAI_PACK_FACTORY_RELEASE_PACK_010.zip --out _out/TEAM_PACK.zip --trace E2
```
