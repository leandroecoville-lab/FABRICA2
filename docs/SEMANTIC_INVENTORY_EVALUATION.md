# Avaliação do inventário_semantic.placeholder.json

O arquivo atual funciona como um **inventário de integridade** (lista + hashes + tamanho),
mas ainda não é um “inventário semântico” completo.

Pontos fortes:
- Permite identificar artefatos e detectar mudanças por sha256.

Lacunas (para virar semântico de verdade):
- Falta `module`/`domain` (ex.: meetcore, connect, app, culture-people).
- Falta `tags`/`keywords` e `summary` (resumo por arquivo).
- Falta `links` entre artefatos (ex.: blueprint -> contrato -> código -> runbook).

Recomendação: evoluir para `inventory.machine.v2.json` com campos:
- id (uuid estável)
- path_hash (hash do path, se precisar blindar)
- kind, bytes, sha256
- module, category (blueprint|code|data|sheet|runbook|tests)
- tags[], keywords[], summary
- relationships[] (depends_on, supersedes, relates_to)
