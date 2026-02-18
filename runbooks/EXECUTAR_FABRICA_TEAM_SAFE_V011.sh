#!/usr/bin/env bash
set -euo pipefail

# ================================================
# EXECUTAR_FABRICA_TEAM_SAFE_V011
# ================================================
#
# Objetivo:
# - Gerar pack0 por módulo
# - Validar (gate) + run-report + approval + merge promoted (leader_ops_snapshot)
# - Exportar team_pack0_<module>.zip (pack0_only)
# - Rodar leak-check HARD (no_leak) antes de entregar ao time
#
# Uso:
#   MODULE=lai-connect LAI_ACTOR_ID=leandro ./runbooks/EXECUTAR_FABRICA_TEAM_SAFE_V011.sh
#
# Modules:
#   meetcore | lai-connect | app-lai | culture-people
#

LAI_PACK_ZIP="${LAI_PACK_ZIP:-}"   # opcional: entrada externa (não obrigatório para plan-pack0)
MODULE="${MODULE:-lai-connect}"
TRACE="${TRACE:-V011_$(date +%Y%m%d_%H%M%S)}"
OUT="${OUT:-./_out}"
TMP="${TMP:-./_tmp}"
POLICY_JSON="${POLICY_JSON:-./governance/audience_policy.team_pack0_only.v1.json}"

mkdir -p "$OUT" "$TMP"

echo "[V011] trace=$TRACE module=$MODULE"

# 0) Testes (recomendado antes de operar)
PYTHONPATH=services/pack-factory python -m pytest -q

# 1) PLAN-PACK0 (módulo)
PYTHONPATH=services/pack-factory python -m app.cli plan-pack0   --module "$MODULE"   --out "$OUT"   --trace "${TRACE}_P0"

PACK0_ZIP="$OUT/pack0-${MODULE}-0.0.1.zip"
test -f "$PACK0_ZIP"

# 2) VALIDATE-PACK0 (gate objetivo)
VALIDATE_JSON="$OUT/validate_${MODULE}.json"
PYTHONPATH=services/pack-factory python -m app.cli validate-pack0   --target "$PACK0_ZIP"   --out "$VALIDATE_JSON"   --trace "${TRACE}_VAL"

python - <<PY
import json
p="${VALIDATE_JSON}"
obj=json.load(open(p,"r",encoding="utf-8"))
assert obj.get("ok") is True, obj
print("[OK] validate-pack0")
PY

# 3) RUN-REPORT (recibo)
RUN_REPORT_JSON="$OUT/run_report_${MODULE}.json"
PYTHONPATH=services/pack-factory python -m app.cli run-report   --target "$PACK0_ZIP"   --out "$RUN_REPORT_JSON"   --trace "${TRACE}_RR"

python - <<PY
import json
p="${RUN_REPORT_JSON}"
obj=json.load(open(p,"r",encoding="utf-8"))
assert obj.get("result") == "pass", obj
print("[OK] run-report")
PY

# 4) APPROVAL (líder) — promoted merge só com isso
APPROVAL_JSON="$OUT/approval_${MODULE}.json"
PYTHONPATH=services/pack-factory python -m app.cli approve-pack   --target "$PACK0_ZIP"   --run-report "$RUN_REPORT_JSON"   --out "$APPROVAL_JSON"   --actor "${LAI_ACTOR_ID:-unknown}"   --trace "${TRACE}_AP"

# 5) PATCH PACKS append-only
PATCH_RR_ZIP="$OUT/patch_rr_${MODULE}.zip"
PATCH_AP_ZIP="$OUT/patch_ap_${MODULE}.zip"

PYTHONPATH=services/pack-factory python -m app.cli wrap-run-report   --in "$RUN_REPORT_JSON"   --out "$PATCH_RR_ZIP"   --trace "${TRACE}_WRR"

PYTHONPATH=services/pack-factory python -m app.cli wrap-approval   --in "$APPROVAL_JSON"   --out "$PATCH_AP_ZIP"   --trace "${TRACE}_WAP"

# 6) MERGE PROMOTED (leader_ops_snapshot)
LEADER_SNAPSHOT="$OUT/leader_ops_snapshot_${MODULE}.zip"

PYTHONPATH=services/pack-factory python -m app.cli merge   --mode promoted   --inputs "$PACK0_ZIP" "$PATCH_RR_ZIP" "$PATCH_AP_ZIP"   --out "$LEADER_SNAPSHOT"   --tmp "$TMP"   --trace "${TRACE}_MERGE"

test -f "$LEADER_SNAPSHOT"

# 7) GATE-NEXT (sequência determinística)
GATE_JSON="$OUT/gate_next_${MODULE}.json"
PYTHONPATH=services/pack-factory python -m app.cli maint gate-next   --snapshot "$LEADER_SNAPSHOT"   --expected pack1   --out "$GATE_JSON"   --trace "${TRACE}_GATE"

python - <<PY
import json
p="${GATE_JSON}"
obj=json.load(open(p,"r",encoding="utf-8"))
assert obj.get("ok") is True, obj
print("[OK] gate-next")
PY

# 8) EXPORT TEAM (pack0_only, default-deny) + LEAK-CHECK HARD
TEAM_PACK0="$OUT/team_pack0_${MODULE}.zip"
LEAK_REPORT="$OUT/leak_report_${MODULE}.json"

PYTHONPATH=services/pack-factory python -m app.cli export-team-pack   --in "$LEADER_SNAPSHOT"   --out "$TEAM_PACK0"   --policy "$POLICY_JSON"   --trace "${TRACE}_TEAM"

PYTHONPATH=services/pack-factory python -m app.cli leak-check   --target "$TEAM_PACK0"   --policy "$POLICY_JSON"   --out "$LEAK_REPORT"   --trace "${TRACE}_LEAK"

echo ""
echo "✅ ENTREGUE:"
echo " - TEAM PACK0 (team-safe): $TEAM_PACK0"
echo " - LEADER OPS SNAPSHOT:    $LEADER_SNAPSHOT"
echo " - RUN_REPORT:             $RUN_REPORT_JSON"
echo " - LEAK_REPORT:            $LEAK_REPORT"
echo " - GATE_NEXT:              $GATE_JSON"
