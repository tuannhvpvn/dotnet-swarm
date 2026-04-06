"""
MigrationReporter — State-Direct reporting engine.
All report values come from MigrationState fields ONLY.
No LLM calls. No inferred text. No "chắc ổn".
"""
import yaml
from app.core.state import MigrationState


class MigrationReporter:

    def phase_summary(self, state: MigrationState) -> str:
        """SOP Section 10 — Phase Summary Report (Markdown)."""
        executed = [t for t in state.tasks]
        passed = [t for t in state.tasks if t.status == "completed"]
        failed = [t for t in state.tasks if t.status == "failed"]

        lines = [
            f"# Migration Phase Summary",
            f"",
            f"**Migration ID:** `{state.migration_id}`",
            f"**Solution Path:** `{state.solution_path}`",
            f"**Phase:** `{state.current_phase}`",
            f"",
            f"## Tasks Executed ({len(executed)})",
        ]
        for t in executed:
            lines.append(f"- [{t.status.upper()}] `{t.id}` — {t.title}")

        lines += ["", f"## Passed ({len(passed)})"]
        for t in passed:
            lines.append(f"- `{t.id}` — {t.title}")

        lines += ["", f"## Failed ({len(failed)})"]
        for t in failed:
            lines.append(f"- `{t.id}` — {t.title}")
            for log in t.logs[-3:]:  # last 3 log entries
                lines.append(f"  - {log}")

        lines += ["", f"## Build Errors ({len(state.build_errors)})"]
        for e in state.build_errors:
            lines.append(f"- `[{e.error_code}]` {e.file_path}:{e.line_number} — {e.message}")

        lines += ["", f"## Fix Attempts"]
        lines.append(f"Total fixes applied: {state.fix_attempts}")

        lines += ["", f"## Debt Items ({len(state.debt)})"]
        for d in state.debt:
            resolved = "✅" if d.resolved else "⬜"
            lines.append(f"- {resolved} `{d.id}` [{d.phase}] — {d.description}")

        return "\n".join(lines)

    def task_detail_yaml(self, state: MigrationState) -> str:
        """Task Detail Report (YAML)."""
        data = [t.model_dump() for t in state.tasks]
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)

    def error_fix_log(self, state: MigrationState) -> str:
        """Error & Fix Log (Markdown table)."""
        lines = [
            "# Error & Fix Log",
            "",
            "| Error Code | File | Line | Message |",
            "|---|---|---|---|",
        ]
        for e in state.build_errors:
            line_num = e.line_number if e.line_number is not None else "—"
            lines.append(f"| `{e.error_code}` | `{e.file_path}` | {line_num} | {e.message} |")
        if not state.build_errors:
            lines.append("| — | — | — | No errors recorded |")
        return "\n".join(lines)

    def debt_register_yaml(self, state: MigrationState) -> str:
        """Debt Register (YAML)."""
        data = [d.model_dump() for d in state.debt]
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)

    def pr_description(self, state: MigrationState) -> str:
        """PR Description (Markdown)."""
        completed = sum(1 for t in state.tasks if t.status == "completed")
        lines = [
            f"# Migration PR: `{state.migration_id}`",
            f"",
            f"**Solution:** `{state.solution_path}`",
            f"**Phase completed:** `{state.current_phase}`",
            f"",
            f"## Summary",
            f"- Tasks completed: {completed}/{len(state.tasks)}",
            f"- Build errors: {len(state.build_errors)}",
            f"- Debt items: {len(state.debt)}",
            f"- Patterns learned: {len(state.learned_patterns)}",
            f"- Fix attempts: {state.fix_attempts}",
        ]
        return "\n".join(lines)

    def evolution_report(self, state: MigrationState) -> str:
        """Evolution Report — SONA patterns learned (Markdown table)."""
        lines = [
            "# SONA Evolution Report",
            "",
            "| Pattern ID | Summary |",
            "|---|---|",
        ]
        for key, value in state.learned_patterns.items():
            lines.append(f"| `{key}` | {value} |")
        if not state.learned_patterns:
            lines.append("| — | No patterns learned yet |")
        return "\n".join(lines)

    def generate_all(self, state: MigrationState) -> dict[str, str]:
        """Generate all report types and register them in state.reports."""
        reports = {
            "phase_summary": self.phase_summary(state),
            "task_detail_yaml": self.task_detail_yaml(state),
            "error_fix_log": self.error_fix_log(state),
            "debt_register_yaml": self.debt_register_yaml(state),
            "pr_description": self.pr_description(state),
            "evolution_report": self.evolution_report(state),
        }
        # Register in state so done_criteria_check gate passes
        for name in reports:
            if name not in state.reports:
                state.reports.append(name)
        return reports
