# 300 Franchising, a maior do mundo e nossa missão

## LAI Pack Factory — RELEASE PACK 011
**trace_id:** LAI-V011-F5AF89B4

Este RELEASE PACK entrega o núcleo executável da **fábrica de software por Packs** (pack-first / padrão Big Tech):
- Geração de **Pack0 (planejamento padrão SRS)** por módulo (`plan-pack0` / alias `pack0`)
- **Conformidade automática do Pack0** (`validate-pack0`) com relatório de lacunas (gate objetivo)
- **Merge determinístico** de múltiplos packs (`merge`)
  - gera automaticamente **Software Book** + **FileMap** em `docs/public/`
- Workflow de **OCA** para correções/patches (`oca-new`)
- Diagnóstico e inventário (`diag`, `inventory-scan`)
- Auditoria e contratos CloudEvents (contratos-first)

### 1 comando para rodar (local)
```bash
make up
```

### 1 comando para rodar testes
```bash
make test
```

### Exemplos (dentro do container)
```bash
# gerar Pack0 de meetcore
docker compose -f infra/docker-compose.yml run --rm pack-factory \
  pack0 --module meetcore --out /data/out --trace LAI-V009-6F8570C9

# validar Pack0
docker compose -f infra/docker-compose.yml run --rm pack-factory \
  validate-pack0 --target /data/in/pack0_meetcore.zip --out /data/out/pack0_validation.json --trace LAI-V009-6F8570C9

# merge packs (gera Software Book automaticamente)
docker compose -f infra/docker-compose.yml run --rm pack-factory \
  merge --inputs /data/in/pack1.zip /data/in/pack1_1.zip --out /data/out/snapshot.zip --tmp /data/tmp --trace LAI-V009-6F8570C9
```

## Novidades nesta release
- **DoD formalizado** (checklist objetivo) + Pack0 já inclui DoD
- **Gate de conformidade** do Pack0 (validate-pack0)
- **Software Book automático no merge** (reduz medo do time e acelera manutenção)



## Novidades nesta release (007)
- Gate MeetCore no Pack0: exige slices + budgets + matriz de retenção (validator objetivo).
- Orquestrador do GPT Builder hard-gated por `history/chain_state.json` (`blocking_reasons`).
- Manual por papel: Lucas/João/Breno (runbooks).
