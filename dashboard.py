import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="🧬 Migration Swarm Dashboard", layout="wide")
st.title("🧬 .NET Migration Swarm — Live Dashboard")
st.markdown("**Queen-led Swarm + GitNexus + SOPEnforcer + Ruflo MCP**")

TASK_ICONS = {
    "completed": "✅",
    "failed": "❌",
    "in_progress": "🔄",
    "pending": "⏳",
    "blocked": "⛔",
}

placeholder = st.empty()

while True:
    state_file = Path("state/current_state.json")
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}

    with placeholder.container():
        # ── Header metrics ──────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Migration ID", state.get("migration_id", "N/A"))
        col2.metric("Phase", state.get("current_phase", "survey").upper())
        workflow = state.get("workflow_state", "normal")
        col3.metric("Workflow", workflow.upper())
        human_gate = "⏸️ WAITING" if state.get("human_decision") == "pending" else "✅ Running"
        col4.metric("Human Gate", human_gate)

        if state.get("blocked_reason"):
            st.error(f"⛔ BLOCKED: {state.get('blocked_reason')}")
            st.info("Run `python main.py approve <path>` to resume.")

        st.divider()

        # ── Task progress ────────────────────────────────────────────────
        tasks = state.get("tasks", [])
        st.subheader(f"📋 Tasks ({len(tasks)} total)")
        if tasks:
            completed = sum(1 for t in tasks if t.get("status") == "completed")
            st.progress(completed / len(tasks) if tasks else 0, f"{completed}/{len(tasks)} completed")

            for task in tasks:
                icon = TASK_ICONS.get(task.get("status", "pending"), "⏳")
                st.write(f"{icon} `{task.get('id', '?')}` — {task.get('title', '?')} [{task.get('status', 'pending')}]")
        else:
            st.info("No tasks yet. Start a migration first.")

        st.divider()

        # ── Build errors ─────────────────────────────────────────────────
        st.subheader("🔧 Build Errors")
        build_errors = state.get("build_errors", [])
        if build_errors:
            for e in build_errors:
                st.error(f"`[{e.get('error_code', '?')}]` {e.get('file_path', '?')}:{e.get('line_number', '?')} — {e.get('message', '?')}")
            st.metric("Fix Attempts", state.get("fix_attempts", 0))
        else:
            st.success("✅ No build errors.")

        st.divider()

        # ── Debt register ─────────────────────────────────────────────────
        st.subheader("📝 Debt Register")
        debt = state.get("debt", [])
        if debt:
            for d in debt:
                icon = "✅" if d.get("resolved") else "⬜"
                st.write(f"{icon} `{d.get('id', '?')}` [{d.get('phase', '?')}] — {d.get('description', '?')}")
        else:
            st.success("✅ No debt items.")

        st.divider()

        # ── Safety violations ─────────────────────────────────────────────
        st.subheader("🛡️ Safety Violations")
        violations = state.get("safety_violations", [])
        if violations:
            for v in violations:
                st.warning(f"⚠️ `{v.get('rule_id', '?')}` — {v.get('message', '?')}")
        else:
            st.success("✅ No safety violations.")

        st.divider()

        # ── SONA patterns ─────────────────────────────────────────────────
        st.subheader("🧬 SONA Learned Patterns")
        patterns = state.get("learned_patterns", {})
        if patterns:
            for k, v in patterns.items():
                st.success(f"**{k}:** {v}")
        else:
            st.info("No patterns learned yet.")

        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')} — polling every 2s")

    time.sleep(2)
