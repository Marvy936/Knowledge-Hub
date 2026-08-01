## Čo je Bash automation

Bash je shell a programovací jazyk orientovaný na spúšťanie procesov, prepájanie streams a prácu s Unixovým prostredím. Je vhodný pre menšie orchestration tasks, ktoré skladajú existujúce CLI nástroje. Nie je automaticky bezpečný iba preto, že skript má málo riadkov.

Shell vykonáva viac fáz expanzie: parameter expansion, command substitution, word splitting, pathname expansion a redirections. Quoting určuje, ktoré fázy sa aplikujú. Premenná nepredstavuje typed string argument; po nequoted expanzii môže vzniknúť nula, jeden alebo mnoho arguments.

```bash
file='report final.txt'
rm -- "$file"
```

Úvodzovky zachovajú jeden argument. `--` ukončí parsing options a chráni pathname začínajúci pomlčkou.

Exit status je základný control signal. Nula znamená úspech podľa command contractu, nenulová hodnota failure alebo špecifický outcome. `set -e` nie je úplný exception model a má kontextové výnimky. Bezpečný skript explicitne kontroluje kritické commands, pipeline status a native output.

Robustný automation lifecycle:

```text
parse inputs
→ validate
→ observe current state
→ calculate plan
→ acquire lock
→ apply bounded mutation
→ verify effective state
→ cleanup
→ emit stable result
```

Idempotencia znamená, že opakované vykonanie nad už požadovaným stavom nevytvorí ďalšiu zmenu. Nie každý príkaz musí byť sám idempotentný, ale celý workflow musí observe-nuť stav a rozhodnúť, či je mutation potrebná.

Temporary files sa vytvárajú cez bezpečný mechanizmus ako `mktemp`, cleanup sa viaže na `trap` a writes sa podľa potreby dokončujú atomic rename-om. Lock musí mať jasný scope a stale-owner contract. Log nesmie miešať machine-readable stdout s diagnostickým stderr, ak ho používa ďalší program.

Bash je slabší pri komplexnom dátovom modeli, concurrency, HTTP clients a veľkej testovateľnej doménovej logike. Vtedy je vhodnejšie presunúť jadro do Pythonu alebo iného jazyka a shell ponechať ako tenký entrypoint.