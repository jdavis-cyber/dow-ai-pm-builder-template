#!/bin/bash
set -euo pipefail

# Provider-neutral governed factory wrapper.
#
# Default: assisted mode prints the next legal governed task packet.
# Autonomous provider execution is enabled through an adapter, not by hardcoding
# any LLM runtime into the template.
#
# Examples:
#   ./automation/factory.sh
#   FACTORY_ADAPTER=shell FACTORY_ADAPTER_COMMAND='codex exec --stdin' ./automation/factory.sh
#   FACTORY_ADAPTER=shell FACTORY_ADAPTER_COMMAND='claude -p' ./automation/factory.sh
#   FACTORY_ADAPTER=shell FACTORY_ADAPTER_COMMAND='gemini -p' ./automation/factory.sh
#
# The shell adapter receives the task prompt on stdin and environment variables:
#   FACTORY_TASK_PACKET=/path/to/task-packet.json
#   FACTORY_TASK_PROMPT=<prompt text>

ADAPTER="${FACTORY_ADAPTER:-assisted}"
INTERVAL="${FACTORY_INTERVAL:-5}"
LOOP_FLAG=""

if [[ "${FACTORY_LOOP:-false}" == "true" ]]; then
  LOOP_FLAG="--loop"
fi

echo "🏭 Governed Factory Runner"
echo "Adapter: ${ADAPTER}"
echo "Loop: ${FACTORY_LOOP:-false}"
echo "Provider-neutral contract: factory owns governance; adapter owns model execution."
echo "---------------------------------------------------"

python3 automation/governed_factory.py --adapter "${ADAPTER}" --interval "${INTERVAL}" ${LOOP_FLAG}
