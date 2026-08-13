# Git Three-Way Merge

This challenge starts with a local repository paused during a real text merge conflict. Resolve the integrated application configuration, stage the result, review it, and complete the merge commit.

Work in `/workspace/repo`.

The final `config/app.json` contract is:

- `mode` = `production`
- `replicas` = `3`
- `feature_x` = `true`

The validator checks the final JSON, the Git index, merge state, ancestry, and merge-commit parent structure. Merely deleting conflict markers is not sufficient.

Start with `git status`, `git ls-files -u`, and the stage-1/2/3 forms of `config/app.json`. Finish with `git add`, review `git diff --cached`, commit the merge, then run `check`.
