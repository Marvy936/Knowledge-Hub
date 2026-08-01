## Čo menia reset, revert a restore

Tieto tri commands sa často zamieňajú, pretože všetky môžu „vrátiť zmenu“. V skutočnosti pracujú s odlišnými vrstvami.

**Restore** kopíruje obsah zo zvoleného source tree alebo indexu do working tree a voliteľne do indexu. Je určený najmä na obnovu pathov. Nehýbe branch refom a nevytvára commit.

**Reset** posúva aktuálnu branch alebo `HEAD` na iný commit a podľa mode môže zároveň prepísať index a working tree. Je to ref/index/worktree transformácia. Na unpublished lokálnej branch je veľmi užitočný; na zdieľanej histórii môže vytvoriť divergence a vyžadovať force push.

**Revert** nevpisuje starý stav priamo do minulosti. Vypočíta inverse change vybraného commit-u a vytvorí nový commit nad aktuálnou históriou. Zachováva audit trail a je preto bežnou voľbou pre už publikované commits.

Reset modes:

```text
--soft
posunie ref, index a working tree nechá

--mixed
posunie ref, index nastaví podľa targetu, working tree nechá

--hard
posunie ref, index aj working tree nastaví podľa targetu
```

Neutrálny príklad:

```text
C1---C2---C3  main
```

`git reset --hard C1` posunie lokálny `main` na `C1` a zhodí staged aj working changes, ktoré nie sú v `C1`. Commits C2 a C3 môžu dočasne zostať recoverable cez reflog, ale ref ich už nedrží.

`git revert C3` naopak vytvorí `C4`, ktorého patch ruší efekt C3:

```text
C1---C2---C3---C4
```

História zostáva append-only. Pri revertovaní merge commit-u treba určiť mainline parent, pretože Git musí vedieť, voči ktorej ancestry line má efekt merge-u obrátiť. Neskoršie opätovné mergovanie môže byť prekvapivé, pretože merge commit zostáva súčasťou ancestry.

Pred deštruktívnou operáciou je vhodné vytvoriť recovery ref a pozrieť `git status`, `git diff`, `git diff --cached` a `git reflog`. Recovery nie je argument pre bezhlavé používanie `--hard`; reflog má retention a untracked files nemusí chrániť.