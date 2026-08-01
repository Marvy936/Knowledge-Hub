from pathlib import Path

path = Path("docs/03-git-and-automation/git-automation-practical-walkthrough.md")
text = path.read_text(encoding="utf-8")
old = """## 8. Annotated release tag

```bash
git tag -a v4.2.1 -m 'Atlas Orders 4.2.1'
git show v4.2.1
git push origin v4.2.1
```"""
new = """## 8. Annotated release tag

Release tag vytvára stabilné meno pre presný schválený commit, ale annotated tag nie je iba ďalší branch-like ref. Git vytvorí samostatný tag object s target object ID, type, taggerom, časom a message a `refs/tags/v4.2.1` ukáže na tento tag object. `git show` preto musí potvrdiť tag metadata aj dereferenced commit; push následne publikuje object a tag ref bez presúvania branchu alebo working tree.

```bash
git tag -a v4.2.1 -m 'Atlas Orders 4.2.1'
git show v4.2.1
git push origin v4.2.1
```"""
if old not in text:
    raise RuntimeError("Annotated release tag block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Section 03 closeout applied.")
