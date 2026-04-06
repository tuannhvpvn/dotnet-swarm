from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START, END
from rich.console import Console
from datetime import datetime
from pathlib import Path
from loguru import logger

from app.core.state import MigrationState
from app.core.config import settings
from app.core.persistence import MigrationPersistence
from app.agents import (
    surveyor_node,
    validator_node,
    documenter_node,
    plan_node,
    human_gate_node,
    prepare_node,
    migrate_task_node,
    checkpoint_node,
    fix_node
)

console = Console()

def route_after_checkpoint(state: MigrationState) -> str:
    if state.workflow_state == "blocked":
        return "human_gate"
    return "validator"

def route_after_validate(state: MigrationState) -> str:
    if len(state.build_errors) > 0 and state.fix_attempts < state.max_fix_attempts:
        return "fix"
    
    pending = [t for t in state.tasks if t.status in ["pending", "failed"]]
    if pending:
        return "migrate_task"
    
    return "documenter"

def build_migration_graph(persistence=None):
    workflow = StateGraph(MigrationState)
    
    # 1. Modular Nodes
    workflow.add_node("surveyor", surveyor_node)
    workflow.add_node("planner", plan_node)
    workflow.add_node("human_gate", human_gate_node)
    workflow.add_node("prepare", prepare_node)
    workflow.add_node("migrate_task", migrate_task_node)
    workflow.add_node("checkpoint", checkpoint_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("fix", fix_node)
    workflow.add_node("documenter", documenter_node)

    # 2. SOP Edge Routing Strategy
    workflow.add_edge(START, "surveyor")
    workflow.add_edge("surveyor", "planner")
    workflow.add_edge("planner", "human_gate")
    workflow.add_edge("human_gate", "prepare")
    workflow.add_edge("prepare", "migrate_task")
    workflow.add_edge("migrate_task", "checkpoint")
    
    workflow.add_conditional_edges(
        "checkpoint", 
        route_after_checkpoint, 
        {"human_gate": "human_gate", "validator": "validator"}
    )
    workflow.add_conditional_edges(
        "validator", 
        route_after_validate, 
        {"fix": "fix", "migrate_task": "migrate_task", "documenter": "documenter"}
    )
    
    workflow.add_edge("fix", "validator")
    workflow.add_edge("documenter", END)

    # 3. LangGraph Native Checkpointer (Dual-Write strategy vs MigrationPersistence)
    db_path = Path(settings.solution_path) / "state" / "langgraph_state.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    checkpointer = SqliteSaver.from_conn_string(str(db_path))

    return workflow.compile(checkpointer=checkpointer, interrupt_before=["human_gate"])

def run_migration(solution_path: str, start_phase: int = 1, persistence=None):
    state = MigrationState(
        migration_id=settings.migration_id, 
        solution_path=str(Path(solution_path).resolve())
    )
    graph = build_migration_graph(persistence)
    logger.info(f"🚀 Migration Swarm ID: {state.migration_id}")
    
    config = {"configurable": {"thread_id": state.migration_id}}
    
    # Main run loop
    for event in graph.stream(state, config, stream_mode="values"):
        if persistence:
            persistence.save(event) # Dual-write explicitly
            
    snapshot = graph.get_state(config)
    # Handle the interrupt_before hook natively
    if snapshot.next and "human_gate" in snapshot.next:
        if input("Approve Execution Plan? (y/n): ").lower() == "y":
            for event in graph.stream(None, config, stream_mode="values"):
                if persistence:
                    persistence.save(event)

    logger.success("🎉 Migration Loop terminated (Completed or Paused)!")
    return snapshot.values
