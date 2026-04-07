"""
csproj_resolver.py — Pure Python XML dependency graph resolver + TargetFramework upgrader.

Decision: D-01 (dec_adv01_parse.md) — deterministic XML parsing only, no AI harness.
Decision: D-03 — SDK-style .csproj only. Legacy ToolsVersion= → hard ValueError.
"""
import os
import re
import xml.etree.ElementTree as ET
from loguru import logger

# ── .sln parsing ─────────────────────────────────────────────────────────────

_SLN_PROJECT_RE = re.compile(
    r'Project\("[^"]+"\)\s*=\s*"[^"]+",\s*"([^"]+\.csproj)"',
    re.IGNORECASE,
)


def parse_sln(sln_path: str) -> list[str]:
    """
    Parse a .sln file and return list of absolute .csproj paths found in it.
    Paths are returned exactly as discovered — caller must validate existence.
    """
    sln_path = os.path.normpath(sln_path)
    sln_dir = os.path.dirname(sln_path)
    try:
        with open(sln_path, encoding="utf-8-sig") as f:
            content = f.read()
    except OSError as exc:
        logger.error(f"Cannot read .sln: {sln_path} — {exc}")
        raise

    results: list[str] = []
    for match in _SLN_PROJECT_RE.finditer(content):
        rel = match.group(1).replace("\\", os.sep)
        abs_path = os.path.normpath(os.path.join(sln_dir, rel))
        results.append(abs_path)

    logger.info(f"parse_sln: found {len(results)} project(s) in {os.path.basename(sln_path)}")
    return results


# ── .csproj graph resolver ────────────────────────────────────────────────────

def _parse_csproj(csproj_path: str) -> ET.ElementTree:
    """Parse csproj, raise ValueError on legacy format, ET.ParseError on bad XML."""
    tree = ET.parse(csproj_path)
    root = tree.getroot()
    if "ToolsVersion" in root.attrib:
        raise ValueError(
            f"Legacy .csproj format (ToolsVersion detected) is not supported: {csproj_path}"
        )
    return tree


def resolve_graph(root_path: str, visited: set[str] | None = None) -> list[str]:
    """
    Recursively resolve all transitive ProjectReference paths from root_path.
    Returns an ordered list (dependencies before dependents — post-order DFS).
    Raises ValueError on legacy format. Raises ET.ParseError on corrupt .csproj.
    Missing referenced files are logged and skipped (non-fatal).
    """
    if visited is None:
        visited = set()

    root_path = os.path.normpath(root_path)
    if root_path in visited:
        return []
    visited.add(root_path)

    # Parse XML — may raise ValueError (legacy) or ET.ParseError (corrupt)
    tree = _parse_csproj(root_path)
    root_elem = tree.getroot()
    project_dir = os.path.dirname(root_path)

    children: list[str] = []
    for ref in root_elem.findall(".//ProjectReference"):
        include = ref.get("Include", "").replace("\\", os.sep)
        if not include:
            continue
        abs_ref = os.path.normpath(os.path.join(project_dir, include))
        if not os.path.exists(abs_ref):
            logger.warning(f"ProjectReference not found (skipped): {abs_ref}")
            continue
        children.extend(resolve_graph(abs_ref, visited))

    # Post-order: dependencies first, then self
    return children + [root_path]


def resolve_from_entry(entry_path: str) -> list[str]:
    """
    Entry point for orchestrator. Accepts either a .sln or .csproj path.
    Returns de-duplicated ordered list of all .csproj paths in the dependency graph.
    Raises ValueError on legacy format. Raises ET.ParseError on corrupt file.
    Raises OSError if entry_path does not exist.
    """
    entry_path = os.path.normpath(entry_path)
    if not os.path.exists(entry_path):
        raise OSError(f"Entry path not found: {entry_path}")

    if entry_path.lower().endswith(".sln"):
        csproj_entries = parse_sln(entry_path)
    elif entry_path.lower().endswith(".csproj"):
        csproj_entries = [entry_path]
    else:
        raise ValueError(f"Unsupported file type (must be .sln or .csproj): {entry_path}")

    visited: set[str] = set()
    result: list[str] = []
    for csproj in csproj_entries:
        if not os.path.exists(csproj):
            logger.warning(f"Entry .csproj not found (skipped): {csproj}")
            continue
        result.extend(resolve_graph(csproj, visited))

    logger.info(
        f"resolve_from_entry: {len(result)} unique project(s) resolved "
        f"from {os.path.basename(entry_path)}"
    )
    return result


# ── TargetFramework upgrader ──────────────────────────────────────────────────

_TF_TAGS = {"TargetFramework", "TargetFrameworks"}


def upgrade_target_framework(csproj_path: str, target_tf: str) -> bool:
    """
    Update <TargetFramework> and/or <TargetFrameworks> to target_tf in csproj_path.
    Returns True if any change was made, False if already at target.
    Raises ValueError on legacy format. Raises ET.ParseError on corrupt file.
    """
    tree = _parse_csproj(csproj_path)  # may raise ValueError | ET.ParseError
    root_elem = tree.getroot()
    modified = False

    for tag in _TF_TAGS:
        for elem in root_elem.iter(tag):
            if elem.text != target_tf:
                logger.info(
                    f"Upgrading {tag} in {os.path.basename(csproj_path)}: "
                    f"{elem.text!r} → {target_tf!r}"
                )
                elem.text = target_tf
                modified = True

    if modified:
        # Preserve original encoding without xml_declaration (SDK-style files don't have one)
        tree.write(csproj_path, encoding="unicode", xml_declaration=False)

    return modified


def upgrade_solution(entry_path: str, target_tf: str) -> dict[str, bool]:
    """
    Full orchestration: resolve graph from entry_path, upgrade all .csproj files.
    Returns dict of {csproj_path: was_modified}.
    Raises on legacy format, parse errors, or missing entry.
    """
    projects = resolve_from_entry(entry_path)
    results: dict[str, bool] = {}
    for proj in projects:
        modified = upgrade_target_framework(proj, target_tf)
        results[proj] = modified
        status = "✅ upgraded" if modified else "— already at target"
        logger.info(f"{status}: {os.path.basename(proj)}")
    return results
