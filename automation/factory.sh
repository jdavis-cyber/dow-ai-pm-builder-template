#!/bin/bash

# Factory Runner Wrapper
# Usage: ./automation/factory.sh

# Configuration
# Set your preferred CLI tool here (e.g., "claude", "ollama run llama3", "llm").
# Leave empty for "Assisted Mode" (copy/paste).
LLM_COMMAND="" 

echo "🏭 Factory Runner: Starting Continuous Loop..."
echo "Press [CTRL+C] to stop."

while true; do
    echo "---------------------------------------------------"
    echo "🔎 Scanning Task Board..."
    
    # 1. Generate the Prompt (Ring 2: run_factory exits 3 if the gate blocks the task)
    PROMPT=$(python3 automation/run_factory.py)
    RC=$?

    if [ "$RC" -eq 3 ]; then
        echo "⛔ Governance gate is CLOSED for the next build task. Not dispatching to the LLM."
        echo "   Resolve discovery/documentation or have the Director approve the gate:"
        echo "   python3 automation/approve_gate.py approve --gate <GateN_...> --decision Approved \\"
        echo "       --approver-role 'Executive Sponsor' --approver-name '<you>'"
        echo "⏸️  Pausing loop. Press [Enter] to re-scan after you have acted..."
        read -r
        continue
    fi

    # Check if prompt is empty (no tasks)
    if [ -z "$PROMPT" ]; then
        echo "✅ No pending tasks found. Waiting 10 seconds..."
        sleep 10
        continue
    fi

    echo "🤖 Next Task Identified:"
    echo "$PROMPT"
    echo "---------------------------------------------------"

    # 2. Execute or Assist
    if [ -n "$LLM_COMMAND" ]; then
        echo "🚀 Autonomous Mode: Sending to $LLM_COMMAND..."
        
        # Pipe prompt to LLM and capture output (optional: tee to log)
        echo "$PROMPT" | $LLM_COMMAND
        
        echo "✅ Task execution complete."
        echo "⏳ Cooling down for 5 seconds..."
        sleep 5
    else
        echo "📋 Assisted Mode: Prompt generated above."
        echo "👉 Action: Copy the prompt above, paste into your Agent, and perform the task."
        echo "👉 Then marks the task as [x] in tasks.md to continue."
        echo "⏸️  Pausing loop. Press [Enter] when ready for the next task..."
        read -r
    fi
done
