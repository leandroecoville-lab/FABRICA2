# MODO_CLONE_SONAR (Auditoria Estática - time-safe)

Este modo simula um revisor de qualidade (estilo *Sonar*), focado em **sinais objetivos** de risco operacional e exposição indevida.

## Objetivo
- Detectar **vazamento por arquivo/prefixo** (paths proibidos).
- Detectar **artefatos de build** que não podem ir para release (`__pycache__`, `*.pyc`, `.pytest_cache`).
- Detectar **padrões de risco** em Python (ex.: `eval`, `exec`, leitura irrestrita de diretórios sem allowlist, escrita fora de `_out`/`_tmp`).
- Detectar **drift de governança** (uso de termos fora do dicionário corporativo).

## Checklist (PASS/FAIL)
### 1) Exposição (no_leak)
PASS se:
- ZIP de time **não** contém nenhum item em:
  - `services/pack-factory/`
  - `docs/references/`
  - `02_INVENTORY/semantic_index/`
  - `gpt_builder/`
  - `history/`
- `leak-check` retorna `status=PASS`.

### 2) Higiene do pacote
PASS se:
- Nenhum arquivo `*.pyc` existe.
- Nenhum diretório `__pycache__/` existe.
- Nenhum `.pytest_cache/` existe.

### 3) Política default-deny
PASS se:
- `export-team-pack` **recusa Release Pack** como input (deve exigir snapshot promoted).

### 4) Rastreamento
PASS se:
- outputs de gates possuem `trace_id` coerente (`run_report.json`, `leak_report.json`, `approval.json`).

## Como rodar (operacional)
- Execute o runbook:
  - `runbooks/EXECUTAR_FABRICA_TEAM_SAFE_V011.sh`
- E valide explicitamente:
  - `python -m app.cli leak-check --target <team_pack0.zip> --out leak_report.json`

