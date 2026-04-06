import re
import os
import stat
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal
import yaml
from loguru import logger


@dataclass
class SafetyResult:
    safe: bool
    rule_id: str | None = None
    severity: Literal["critical", "warning", "info"] = "info"
    message: str = ""
    file_path: str | None = None


class SafetyRules:
    """Enforcement module for safety rules — loaded from config/safety.yaml."""

    def __init__(self, config_path: str = "config/safety.yaml"):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        bl = cfg.get("blacklist", {})
        self.blacklist_folders: list[str] = bl.get("folders", [])
        self.blacklist_files: list[str] = bl.get("files", [])
        self.blacklist_content: list[re.Pattern] = [
            re.compile(re.escape(p)) for p in bl.get("content_patterns", [])
        ]
        self.protected_branches: list[str] = cfg.get("git_safety", {}).get("protected_branches", [])
        self.forbidden_sql: list[str] = [kw.upper() for kw in cfg.get("forbidden_sql", [])]
        self.absolute_rules: list[dict] = cfg.get("absolute_rules", [])

    # ── Check methods ────────────────────────────────────────

    def check_file_path(self, path: str) -> SafetyResult:
        """Check nếu file path nằm trong blacklist folders hoặc files."""
        from fnmatch import fnmatch

        normalized = path.replace("\\", "/")
        for pattern in self.blacklist_folders:
            # Pattern dạng "**/keys/" — match bất kỳ segment nào
            clean_pattern = pattern.strip("*").strip("/")
            if f"/{clean_pattern}/" in f"/{normalized}" or normalized.startswith(f"{clean_pattern}/"):
                return SafetyResult(
                    safe=False, rule_id="SAFE-002", severity="critical",
                    message=f"Blacklisted folder: {clean_pattern}/ matched in {path}",
                    file_path=path
                )

        basename = Path(path).name
        for pattern in self.blacklist_files:
            if fnmatch(basename, pattern):
                return SafetyResult(
                    safe=False, rule_id="SAFE-002", severity="critical",
                    message=f"Blacklisted file pattern: {pattern} matched {basename}",
                    file_path=path
                )

        return SafetyResult(safe=True, message="Path clean", file_path=path)

    def check_file_content(self, content: str) -> SafetyResult:
        """Scan nội dung file để phát hiện credential patterns."""
        for pattern in self.blacklist_content:
            match = pattern.search(content)
            if match:
                return SafetyResult(
                    safe=False, rule_id="SAFE-004", severity="critical",
                    message=f"Blacklisted content pattern found: {match.group()}"
                )
        return SafetyResult(safe=True, message="Content clean")

    def check_sql(self, sql: str) -> SafetyResult:
        """Kiểm tra SQL có chứa forbidden write keywords không."""
        upper = sql.upper()
        for kw in self.forbidden_sql:
            # Match keyword ở word boundary
            if re.search(rf"\b{kw}\b", upper):
                return SafetyResult(
                    safe=False, rule_id="SAFE-001", severity="critical",
                    message=f"Forbidden SQL keyword detected: {kw}"
                )
        return SafetyResult(safe=True, message="SQL clean")

    def check_branch(self, branch: str) -> SafetyResult:
        """Kiểm tra branch có nằm trong protected list không."""
        if branch in self.protected_branches:
            return SafetyResult(
                safe=False, rule_id="SAFE-003", severity="critical",
                message=f"Protected branch: {branch}"
            )
        return SafetyResult(safe=True, message="Branch allowed")

    def check_pre_commit(self, staged_files: list[str]) -> list[SafetyResult]:
        """Check tất cả staged files trước khi commit."""
        violations = []
        for f in staged_files:
            result = self.check_file_path(f)
            if not result.safe:
                violations.append(result)
        return violations

    def scan_worktree(self, worktree_path: str) -> list[SafetyResult]:
        """Walk thư mục worktree, kiểm tra mỗi file path và content."""
        violations: list[SafetyResult] = []
        root = Path(worktree_path)

        for dirpath, dirnames, filenames in os.walk(root):
            # Bỏ qua .git
            dirnames[:] = [d for d in dirnames if d != ".git"]

            for fname in filenames:
                fpath = Path(dirpath) / fname
                rel = str(fpath.relative_to(root))

                # Check path
                path_result = self.check_file_path(rel)
                if not path_result.safe:
                    violations.append(path_result)
                    continue

                # Check content (chỉ text files, bỏ qua binary)
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    content_result = self.check_file_content(content)
                    if not content_result.safe:
                        content_result.file_path = rel
                        violations.append(content_result)
                except Exception:
                    pass  # Binary hoặc unreadable — skip

        return violations

    # ── Git Hook ─────────────────────────────────────────────

    def generate_hook_script(self, worktree_path: str) -> str:
        """Tạo nội dung bash pre-commit hook gọi Python safety check."""
        project_root = Path(worktree_path).resolve()
        return f"""#!/bin/bash
# Auto-generated by dotnet-swarm SafetyRules — DO NOT EDIT
cd "{project_root}"
python -m app.core.safety --pre-commit
exit $?
"""

    def install_hook(self, worktree_path: str):
        """Cài đặt pre-commit hook vào worktree."""
        hooks_dir = Path(worktree_path) / ".git" / "hooks"
        if not hooks_dir.exists():
            logger.warning(f"No .git/hooks dir at {worktree_path} — skipping hook install")
            return

        hook_path = hooks_dir / "pre-commit"
        hook_path.write_text(self.generate_hook_script(worktree_path), encoding="utf-8")
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        logger.info(f"✅ Safety pre-commit hook installed: {hook_path}")


# ── CLI entry point (cho git hook) ──────────────────────────

if __name__ == "__main__":
    import sys

    if "--pre-commit" in sys.argv:
        rules = SafetyRules()
        # Lấy staged files từ git
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True
        )
        staged = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        violations = rules.check_pre_commit(staged)

        if violations:
            print("🚫 SAFETY VIOLATION — Commit blocked:")
            for v in violations:
                print(f"  [{v.rule_id}] {v.message}")
            sys.exit(1)

        print("✅ Safety check passed")
        sys.exit(0)
