from pathlib import Path
from rich.console import Console
from loguru import logger

console = Console()

class AutoSkillCreator:
    def __init__(self):
        self.skills_dir = Path(".migration-skills")

    def create_skill(self, skill_name: str, description: str, examples: list = None):
        skill_dir = self.skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        content = f"""---
name: {skill_name}
description: {description}
category: auto-generated
version: 1.0
tags: [auto, pattern]
---

**Mô tả:** {description}

**Rules:**
- Áp dụng khi lỗi tương tự lặp lại nhiều lần.
{chr(10).join([f"- Example: {ex}" for ex in (examples or [])])}

**Khi nào dùng:** Khi Ruflo phát hiện pattern lặp lại ≥ 3 lần.
"""

        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        logger.success(f"🧬 Auto-created skill: {skill_name}")
        console.print(f"[bold magenta]🧬 Tự tạo skill mới: {skill_name}[/]")

        # Sync skill mới
        from app.utils.sync_skills import run as sync_skills
        sync_skills(str(Path.cwd()))
        return True

auto_skill_creator = AutoSkillCreator()
