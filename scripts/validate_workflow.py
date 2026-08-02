#!/usr/bin/env python3
"""Read-only validation for the AI-team workflow handoff contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


CANONICAL = {
    "ceo-request.md": {"CEO_REQUEST_RECORDED"},
    "prd.md": {"PRD_READY", "NEEDS_CLARIFICATION"},
    "architecture.md": {"ARCHITECTURE_READY", "BLOCKED"},
    "implementation-report.md": {"IMPLEMENTATION_COMPLETE", "BLOCKED"},
    "qa-report.md": {"PASS", "FAIL"},
    "review-report.md": {"APPROVED", "CHANGES_REQUIRED"},
    "final-report.md": {"READY_FOR_CEO_REVIEW", "BLOCKED"},
}

REQUIRED_METADATA = (
    "Handoff Contract",
    "Feature Key",
    "Change Package",
    "Attempt",
    "Outcome",
    "Disposition",
    "Next Route",
    "Requirement IDs",
    "Evidence IDs",
    "Input Revisions",
)


def terminal_status(text: str) -> tuple[list[str], str | None]:
    statuses = re.findall(r"^STATUS:\s*([A-Z0-9_]+)\s*$", text, re.MULTILINE)
    last_non_empty = next((line.strip() for line in reversed(text.splitlines()) if line.strip()), None)
    terminal = None
    if last_non_empty:
        match = re.fullmatch(r"STATUS:\s*([A-Z0-9_]+)", last_non_empty)
        if match:
            terminal = match.group(1)
    return statuses, terminal


def metadata(text: str) -> dict[str, str]:
    if "## Handoff Metadata" not in text:
        return {}
    section = text.split("## Handoff Metadata", 1)[1]
    section = section.split("\n## ", 1)[0]
    result: dict[str, str] = {}
    for key in REQUIRED_METADATA:
        match = re.search(rf"^{re.escape(key)}:\s*`?([^`\n]+?)`?\s*$", section, re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()
    return result


def validate(path: Path, strict: bool) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    statuses, terminal = terminal_status(text)
    allowed = CANONICAL[path.name]
    fields = metadata(text)

    if len(statuses) != 1:
        message = f"{path}: expected exactly one STATUS line, found {len(statuses)}"
        (errors if fields or strict else warnings).append(message)
    if terminal is None:
        message = f"{path}: STATUS line is not the final non-empty line"
        (errors if fields or strict else warnings).append(message)
    elif terminal not in allowed:
        message = f"{path}: legacy or unknown terminal status {terminal}"
        (errors if strict else warnings).append(message)

    if fields:
        missing = [key for key in REQUIRED_METADATA if key not in fields]
        if missing:
            errors.append(f"{path}: missing handoff fields: {', '.join(missing)}")
        if fields.get("Handoff Contract") != "v1":
            errors.append(f"{path}: Handoff Contract must be v1")
        if terminal and fields.get("Outcome") and fields["Outcome"] != terminal:
            errors.append(f"{path}: Outcome {fields['Outcome']} does not match STATUS {terminal}")
    else:
        message = f"{path}: no Handoff Metadata (legacy artifact)"
        (errors if strict else warnings).append(message)

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail on legacy artifacts without contract metadata")
    parser.add_argument("--path", type=Path, default=Path("projects"), help="artifact root to scan")
    args = parser.parse_args()

    files = [path for path in args.path.rglob("*.md") if path.name in CANONICAL]
    errors: list[str] = []
    warnings: list[str] = []
    for path in sorted(files):
        file_errors, file_warnings = validate(path, args.strict)
        errors.extend(file_errors)
        warnings.extend(file_warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Validated {len(files)} workflow artifacts: {len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
