# Arquitetura — LAI Pack Factory
**trace_id:** LAI-V009-6F8570C9

## Visão
- **Pack0:** planejamento padrão (SRS) por módulo (RF/RNF/UC/diagramas/rastreabilidade)
- **Pack1:** thin-slice executável (infra + serviços + contratos + testes)
- **PackX.Y:** correções/incrementos via OCA (append-only)
- **MEPLAI:** modo unificado de execução do GPT Builder (humanizado + padronizado)

## Componentes
- Orquestrador (GPT Builder): `gpt_builder/ORQUESTRADOR_MASTER.md`
- Modo Execução Padrão LAI: `gpt_builder/MODO_EXECUCAO_PADRAO_LAI.md`
- CLI `lai-pack`: `services/pack-factory/app/`
- Contratos: `contracts/`
- Infra local: `infra/docker-compose.yml`
- Testes: `tests/`
- Governança: `governance/` + `.github/`

## Gates (v0.4.0)
- **validate-pack0**: garante conformidade do Pack0 (SRS + pack-first)
- **merge**: gera snapshot + `docs/public/SOFTWARE_BOOK.md` + `docs/public/FILEMAP.md`

## Regra central
Tudo que não está em contrato/documento/histórico **não existe**.

