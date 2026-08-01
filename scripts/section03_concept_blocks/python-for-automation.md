## Čo je Python automation

Python je všeobecný programovací jazyk vhodný pre automatizáciu, keď workflow potrebuje bohatší dátový model, HTTP alebo cloud SDK, concurrency, testovateľnosť a presné error handling. Výhodou nie je iba čitateľnejšia syntax; dôležité je, že domain logiku možno oddeliť od I/O a testovať ako čisté funkcie.

Dobrá automatizačná aplikácia oddeľuje vrstvy:

```text
CLI parsing
→ configuration loading
→ domain validation
→ observation adapter
→ planning
→ mutation adapter
→ verification
→ result serialization
```

Configuration sa načíta raz a prevedie na typed alebo aspoň validovaný immutable domain model. Functions nemajú potichu čítať environment variables z rôznych miest, pretože vznikajú skryté inputs a nepredvídateľné tests.

Plan má presne pomenovať subject a expected current state. Pri apply sa current state znovu observe-ne a porovná s plan precondition. Tým sa odhalí stale plan alebo concurrent writer. Mutation result sa nesmie automaticky zameniť za effective-state verification.

Retries patria iba na operations s jasným timeout a idempotency contractom. Network timeout môže mať unknown outcome: server mutation dokončil, ale client response nedostal. Blind retry môže vytvoriť duplicate. Používa sa idempotency key, operation lookup alebo reconciliation.

Exceptions sa zachytávajú na hranici, ktorá ich vie preložiť na stabilný result alebo vykonať recovery. `except Exception: pass` ničí evidence. CLI má definovať exit codes a písať machine-readable result na stdout, diagnostics na stderr.

Atomic local write typicky vytvorí temporary file v rovnakom filesystéme, flushne a podľa durability požiadavky fsyncne data, potom použije `os.replace`. Pri remote systéme atomicitu určuje jeho API, conditional update alebo transaction model.

Packaging a dependencies sú súčasťou reproducibility. Skript, ktorý „funguje na mojom Pythone“, nemá stabilný runtime contract. Pinning, virtual environment alebo packaged executable musí byť spojený s testovanou interpreter a dependency verziou.