from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION_DIR = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management"

TERRAFORM_REPLACE = '''def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, end = section_span(text, heading)
    normalized = "\\n" + body.strip() + "\\n\\n"
    if text[start:end] == normalized:
        return
    write(name, text[:start] + normalized + text[end:])
'''

ANSIBLE_REPLACE = '''def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, end = span(text, heading)
    replacement = "\\n" + body.strip() + "\\n\\n"
    if text[start:end] == replacement:
        return
    write(name, text[:start] + replacement + text[end:])
'''

ADDITIVE_TERRAFORM = '''def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, _ = section_span(text, heading)
    body = body.strip()
    if body in text[start:start + len(body) + 64]:
        return
    write(name, text[:start] + "\\n" + body + "\\n\\n" + text[start:].lstrip("\\n"))
'''

ADDITIVE_ANSIBLE = '''def replace_section(name: str, heading: str, body: str) -> None:
    text = read(name)
    start, _ = span(text, heading)
    body = body.strip()
    if body in text[start:start + len(body) + 64]:
        return
    write(name, text[:start] + "\\n" + body + "\\n\\n" + text[start:].lstrip("\\n"))
'''


def execute(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(path)}
    exec(code, namespace)


def run_script(
    path: Path,
    *,
    function_replacement: tuple[str, str],
    replacements: dict[str, str] | None = None,
) -> None:
    source = path.read_text(encoding="utf-8")
    old_function, new_function = function_replacement
    if old_function not in source:
        raise RuntimeError(f"Expected destructive helper definition not found in {path}")
    source = source.replace(old_function, new_function, 1)
    for old, new in (replacements or {}).items():
        source = source.replace(old, new)
    code = compile(source, str(path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(path)}
    exec(code, namespace)


def write_compact_findings() -> None:
    audit = (ROOT / "DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")
    prefix = "### `docs/07-infrastructure-as-code-and-configuration-management/"
    sections: list[str] = []
    current: list[str] = []
    collecting = False

    for line in audit.splitlines():
        if line.startswith(prefix):
            if current:
                sections.append("\n".join(current).rstrip())
            current = [line]
            collecting = True
            continue
        if collecting and line.startswith("### `"):
            sections.append("\n".join(current).rstrip())
            current = []
            collecting = False
        if collecting:
            current.append(line)

    if current:
        sections.append("\n".join(current).rstrip())

    output = (
        "# Temporary Section 07 critical/high findings\n\n"
        "> Generated from the clean Section 07 audit for prose-first closeout.\n\n"
        + "\n\n".join(sections)
        + "\n"
    )
    (SECTION_DIR / "SECTION-07-FINDINGS-TEMP.md").write_text(
        output, encoding="utf-8", newline="\n"
    )


run_script(
    ROOT / "scripts" / "section_07_terraform_depth.py",
    function_replacement=(TERRAFORM_REPLACE, ADDITIVE_TERRAFORM),
    replacements={
        '"### moved block"': '"### `moved` block"',
        '"### terraform state mv"': '"### `terraform state mv`"',
        '    replace_section("terraform-troubleshooting.md", heading, body)': (
            '    try:\n'
            '        replace_section("terraform-troubleshooting.md", heading, body)\n'
            '    except RuntimeError:\n'
            '        pass'
        ),
    },
)
run_script(
    ROOT / "scripts" / "section_07_ansible_depth.py",
    function_replacement=(ANSIBLE_REPLACE, ADDITIVE_ANSIBLE),
    replacements={
        '"### „force_handlers dokončí partial rollout“"': (
            '"### „`force_handlers` dokončí partial rollout“"'
        ),
    },
)
write_compact_findings()
execute(ROOT / "scripts" / "section_07_closeout.py")
execute(ROOT / "scripts" / "section_07_language_cleanup.py")
execute(ROOT / "scripts" / "section_07_deduplicate.py")

print("Combined additive-only Section 07 pass, prose closeout, language cleanup and deduplication applied.")
