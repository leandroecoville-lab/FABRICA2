# Ciclo de vida: Pack0 → Pack1 → PackX.Y

- **Pack0 (planejamento padrão)**: descreve arquitetura, contratos e DoD do módulo.
- **Pack1 (thin-slice executável)**: código rodando + infra + testes + docs + runbooks.
- **PackX.Y (correções/incrementos)**: sempre via OCA (REPORT/PATCH), gerando novo snapshot.

Regras de sobrevivência:
- Sem OCA obrigatório, o sistema vira Frankenstein.
- Sem Prompt de Continuidade dentro do pack, o GPT “deriva” quando muda de chat.
- Sem gates (run/test/docs/manifest/audit), o pack não promove.


## Gates objetivos (v0.4.0+)
- Pack0: `lai-pack validate-pack0` (conformidade SRS + estrutura pack-first)
- Snapshot/Merge: `lai-pack merge` gera automaticamente `docs/public/SOFTWARE_BOOK.md` + `docs/public/FILEMAP.md`

