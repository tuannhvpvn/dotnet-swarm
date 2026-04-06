from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from rich.console import Console
from datetime import datetime
from pathlib import Path
from loguru import logger

from app.core.state import MigrationState
from app.core.config import settings
from app.core.ruflo_mcp import ruflo_client
from app.core.persistence import MigrationPersistence
from app.agents import surveyor_node, phase1_migrator_node, phase2_modernizer_node, validator_node, documenter_node
from app.integrations.vibekanban_adapter import vibekanban

console = Console()

def supervisor_node(state: MigrationState, persistence: MigrationPersistence = None) -> Command:
    logger.info(f"👑 Queen Supervisor | Phase: {state.current_phase}")
    console.print("[bold green]👑 Queen Supervisor (Ruflo) đang điều phối...[/]")

    if state.error_log:
        reasoning = ruflo_client.get_reasoning(f"Phase: {state.current_phase} | Errors: {len(state.error_log)}")
        logger.info(f"Ruflo Reasoning: {reasoning[:150]}...")

    next_node = ruflo_client.route_task(state, "default")
    vibekanban.update_agent("Queen Supervisor", "👑 Routing", next_node=next_node)

    if state.current_phase == "phase1" and state.phase_progress.get("phase1", 0) >= 100:
        state.needs_human_approval = True
        vibekanban.push("human_gate", {"phase": "phase1"})
        if persistence:
            persistence.save(state)
        return Command(goto=END, update=state)

    if persistence:
        persistence.save(state)

    state.last_updated = datetime.now()
    return Command(goto=next_node, update={"current_phase": state.current_phase})

def build_migration_graph(persistence=None):
    workflow = StateGraph(MigrationState)
    workflow.add_node("supervisor", lambda s: supervisor_node(s, persistence))
    workflow.add_node("surveyor", surveyor_node)
    workflow.add_node("phase1_migrator", phase1_migrator_node)
    workflow.add_node("phase2_modernizer", phase2_modernizer_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("documenter", documenter_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges("supervisor", lambda s: s.current_phase, {"survey": "surveyor", "phase1": "phase1_migrator", "phase2": "phase2_modernizer"})

    for worker in ["surveyor", "phase1_migrator", "phase2_modernizer"]:
        workflow.add_edge(worker, "validator")
        workflow.add_edge("validator", "documenter")
        workflow.add_edge("documenter", "supervisor")

    return workflow.compile(checkpointer=MemorySaver())

def run_migration(solution_path: str, start_phase: int = 1, persistence=None):
    state = MigrationState(migration_id=settings.migration_id, solution_path=str(Path(solution_path).resolve()), current_phase="survey" if start_phase == 1 else "phase2")
    graph = build_migration_graph(persistence)
    logger.info(f"🚀 Migration Swarm ID: {state.migration_id}")
    for event in graph.stream(state, stream_mode="values"):
        if getattr(event, "needs_human_approval", False):
            if input("Approve Phase 2? (y/n): ").lower() != "y":
                break
            event.needs_human_approval = False
            event.current_phase = "phase2"
    if persistence:
        persistence.save(event)
    logger.success("🎉 Migration hoàn tất!")
    return event
