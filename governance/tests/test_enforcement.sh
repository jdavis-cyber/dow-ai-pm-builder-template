#!/bin/bash
# End-to-end verification of the governance enforcement layer.
# Runs hermetically against a TEMP copy of gate_state.json (never mutates the
# committed seed) using a throwaway signing secret. Stdlib/CLI only.
#
# Usage: bash governance/tests/test_enforcement.sh
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)")"
cd "$ROOT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp .governance/gate_state.json "$TMP/gate_state.json"

export DOW_GATE_STATE="$TMP/gate_state.json"
export DOW_GATE_SECRET="test-secret-$(date +%s)"   # throwaway; never the real key

GK="python3 automation/gatekeeper.py"
AP="python3 automation/approve_gate.py"
PASS=0; FAIL=0

assert_rc() {  # assert_rc <want> <desc>   (compares against global RC)
  if [ "$RC" -eq "$1" ]; then echo "PASS: $2"; PASS=$((PASS+1));
  else echo "FAIL: $2 (want rc=$1 got rc=$RC)"; FAIL=$((FAIL+1)); fi
}
hook() { echo "$2" | $GK hook --runtime "$1" >/dev/null 2>&1; RC=$?; }
gate_status() {  # set gate status (optionally clearing approval) in temp state
  python3 - "$DOW_GATE_STATE" "$1" "$2" <<'PY'
import json,sys
p,status,clear=sys.argv[1],sys.argv[2],sys.argv[3]
s=json.load(open(p)); g=s["gates"]["Gate1_BusinessUnderstanding"]
g["status"]=status
if clear=="clear": g["approval"]=None; g["ready_for_verification_by"]=None
json.dump(s,open(p,"w"),indent=2)
PY
}

echo "== Lock 0 =="
$GK refresh-lock0 >/dev/null 2>&1; RC=$?; assert_rc 0 "spec validation recorded"

echo "== Closed-gate blocks builds, all runtimes =="
hook claude '{"tool_name":"Write","tool_input":{"file_path":"execution/app.py"}}'; assert_rc 2 "claude: Write execution/ -> deny"
hook gemini '{"name":"WriteFile","args":{"file_path":"execution/app.py"}}';        assert_rc 2 "gemini: WriteFile execution/ -> deny"
hook codex  '{"tool":"apply_patch","input":{"input":"*** Add File: execution/x.py"}}'; assert_rc 2 "codex: apply_patch execution/ -> deny"

echo "== Discovery + reads always allowed =="
hook claude '{"tool_name":"Write","tool_input":{"file_path":"docs/interviews/x.md"}}'; assert_rc 0 "claude: Write docs/ -> allow"
hook claude '{"tool_name":"Read","tool_input":{"file_path":"execution/app.py"}}';      assert_rc 0 "claude: Read execution/ -> allow"

echo "== Protected state file cannot be written by an agent =="
hook gemini '{"name":"WriteFile","args":{"file_path":".governance/gate_state.json"}}'; assert_rc 2 "gemini: Write gate_state.json -> deny"
hook claude '{"tool_name":"Bash","tool_input":{"command":"echo x >> .governance/gate_state.json"}}'; assert_rc 2 "claude: Bash append gate_state.json -> deny"

echo "== Forgery rejected =="
gate_status "Approved" "clear"   # status flipped, NO signature
$GK verify-consistency >/dev/null 2>&1; RC=$?; assert_rc 1 "verify-consistency detects forged Approved"
$GK check-action --tool Write --path execution/app.py >/dev/null 2>&1; RC=$?; assert_rc 2 "forged Approved still blocks execution/"
gate_status "Not Approved" "clear"

echo "== mark-ready is the agent ceiling (NOT an approval) =="
$AP mark-ready --gate Gate1_BusinessUnderstanding --by scrum-master >/dev/null 2>&1; RC=$?; assert_rc 0 "mark-ready succeeds"
$GK check-action --tool Write --path execution/app.py >/dev/null 2>&1; RC=$?; assert_rc 2 "READY FOR VERIFICATION still blocks builds"
gate_status "Not Approved" "clear"

echo "== Signed approval opens the gate =="
$AP approve --gate Gate1_BusinessUnderstanding --decision Approved \
   --approver-role "Executive Sponsor" --approver-name "Test Director" >/dev/null 2>&1
$GK verify-consistency >/dev/null 2>&1; RC=$?; assert_rc 0 "approve_gate writes a valid signature"
$GK check-action --tool Write --path execution/app.py >/dev/null 2>&1; RC=$?; assert_rc 0 "approved gate ALLOWS execution/ write"

echo "== Tamper after signing is caught =="
python3 - "$DOW_GATE_STATE" <<'PY'
import json,sys
p=sys.argv[1]; s=json.load(open(p))
s["gates"]["Gate1_BusinessUnderstanding"]["approval"]["conditions"]="ALTERED"
json.dump(s,open(p,"w"),indent=2)
PY
$GK verify-consistency >/dev/null 2>&1; RC=$?; assert_rc 1 "tampered approval fails verification"
$GK check-action --tool Write --path execution/app.py >/dev/null 2>&1; RC=$?; assert_rc 2 "tampered approval re-closes the gate"

echo "== Lock 0 failure blocks even an approved gate =="
gate_status "Not Approved" "clear"
$AP approve --gate Gate1_BusinessUnderstanding --decision Approved \
   --approver-role "Executive Sponsor" --approver-name "Test Director" >/dev/null 2>&1
python3 - "$DOW_GATE_STATE" <<'PY'
import json,sys
p=sys.argv[1]; s=json.load(open(p)); s["lock0_spec_validation"]["status"]="FAIL"
json.dump(s,open(p,"w"),indent=2)
PY
$GK check-action --tool Write --path execution/app.py >/dev/null 2>&1; RC=$?; assert_rc 2 "Lock0 FAIL blocks execution/ despite approval"

echo
echo "==================================================="
echo "RESULT: $PASS passed, $FAIL failed"
if [ "$FAIL" -eq 0 ]; then echo "ALL ENFORCEMENT CHECKS PASSED"; else echo "ENFORCEMENT CHECKS FAILED"; fi
exit "$FAIL"
