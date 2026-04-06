import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="🧬 Migration Swarm Dashboard", layout="wide")
st.title("🧬 .NET Migration Swarm Live Dashboard")
st.markdown("**Queen-led Swarm + GitNexus + Self-Evolution + Vibekanban**")

placeholder = st.empty()

while True:
    state_file = Path("state/current_state.json")
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}

    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Migration ID", state.get("migration_id", "N/A"))
        col2.metric("Current Phase", state.get("current_phase", "survey").upper())
        col3.metric("Human Gate", "⏸️ WAITING" if state.get("needs_human_approval") else "✅ Running")

        st.progress(state.get("phase_progress", {}).get("phase1", 0)/100, "Phase 1 - Lift & Shift")
        st.progress(state.get("phase_progress", {}).get("phase2", 0)/100, "Phase 2 - Modernize")

        st.subheader("👑 Agent Status")
        agents = ["Surveyor", "Phase1 Migrator", "Phase2 Modernizer", "Validator", "Documenter"]
        for agent in agents:
            st.write(f"• {agent}: Running")

        st.subheader("🧬 Self-Evolution (Ruflo ReasoningBank)")
        for k, v in state.get("learned_patterns", {}).items():
            st.success(f"{k}: {v}")

        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

    time.sleep(2)
