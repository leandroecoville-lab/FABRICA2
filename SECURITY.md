# SECURITY — LAI Pack Factory

## Princípios
- **Audit append-only**: logs e artefatos de decisão devem ser rastreáveis (trace_id).
- **Segredos fora do código**: nada de tokens/chaves dentro do repositório.
- **Sem obfuscação de intenção**: dicionário de termos sensíveis é para padronização corporativa, não para burlar compliance.

## Segurança Operacional (team-safe)
- Não compartilhe o Release Pack completo com o time.
- Use:
  - `export-manual` (somente o manual)
  - `export-team-pack` (ZIP filtrado team-safe)

## Externalização
- `docs/references/` e `02_INVENTORY/semantic_index/` foram externalizados no RELEASE PACK 010.
- Ledger: `docs/references/EXTERNAL_INPUTS.md` (sha256 + bytes).
