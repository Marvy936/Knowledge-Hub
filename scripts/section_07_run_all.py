from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(path: Path, replacements: dict[str, str] | None = None) -> None:
    source = path.read_text(encoding="utf-8")
    for old, new in (replacements or {}).items():
        source = source.replace(old, new)
    code = compile(source, str(path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(path)}
    exec(code, namespace)


# Run both idempotent section passes from the current branch head.
run_script(
    ROOT / "scripts" / "section_07_terraform_depth.py",
    {
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
run_script(ROOT / "scripts" / "section_07_ansible_depth.py")

print("Combined Section 07 explanation-depth pass applied.")
