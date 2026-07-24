# journald and Logging

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [systemd, services a daemons](systemd-services-daemons.md), [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: observability, log rotation, incident response, centralized logging

## 1. Logging ako event pipeline

Logging je proces, ktorým emitter vytvorí záznam o udalosti a odovzdá ho do transportu, lokálneho store alebo centralizovaného systému. Hodnota logu nevzniká iba textom správy; závisí aj od času, identity procesu, služby, priority, bootu a kontextu, ktorý umožní udalosť korelovať s ostatnými dôkazmi.

`systemd-journald` je lokálna service, ktorá prijíma records z viacerých transportov, dopĺňa dôveryhodné metadata, ukladá ich do journal files a sprístupňuje query cez `journalctl`.

```text
emitter
  ↓ stdout/stderr, syslog, native API, kernel
transport
  ↓
journald
  ├── metadata enrichment
  ├── rate limiting
  ├── indexing
  ├── volatile/persistent storage
  └── optional forwarding
  ↓
local query / collector / SIEM
```

## 2. Journal record nie je iba textový riadok

Record môže obsahovať `MESSAGE=` a ďalšie fields. Journald zároveň pridáva trusted fields odvodené z process credentials, cgroup a kernel contextu, napríklad `_PID`, `_UID`, `_SYSTEMD_UNIT`, `_EXE`, `_BOOT_ID` alebo `_TRANSPORT`.

Tieto metadata umožňujú filtrovať podľa identity a lifecycle služby aj vtedy, keď text správy neobsahuje názov aplikácie. Textový log file bez stabilnej štruktúry často vyžaduje nepresný regex a manuálnu koreláciu.

Nie všetky fields majú rovnakú dôveryhodnosť. Aplikácia môže poslať vlastné field names, ale underscore-prefixed trusted fields typicky dopĺňa journald podľa pozorovaného runtime contextu.

## 3. Zdroje records a ich failure boundaries

### stdout a stderr systemd služby

Systemd môže pripojiť descriptors služby na journal. Aplikácia potom nemusí riešiť súbor, rotation ani owner pathu; zapisuje do štandardných streams a manager zachová unit context.

To však neznamená, že každý write sa bezpečne uloží. Proces môže byť ukončený pred flushom user-space bufferu, journald môže uplatniť rate limit alebo storage môže byť nedostupný.

### Syslog transport

Tradičné aplikácie posielajú records cez syslog socket a používajú facility a priority semantics. Journald ich môže prijať a následne forwardovať do rsyslog alebo syslog-ng podľa host policy.

### Native journal API

Native API podporuje structured fields priamo pri emitovaní. Je vhodná, keď aplikácia potrebuje odovzdať request ID, tenant, component alebo iný machine-queryable context bez parsovania message textu.

### Kernel transport

Kernel records pochádzajú z ring bufferu a obsahujú informácie o devices, filesystems, OOM, drivers a security denials. Journald ich môže uložiť spolu s boot metadata, ale kernel ring buffer a persistent journal majú odlišný lifetime.

## 4. Journald je lokálny event store, nie celý observability systém

Journald rieši host-local ingestion, metadata enrichment, storage a query. Nezaručuje dlhodobú fleet-wide retenciu, cross-host search, tenant isolation ani analytické indexovanie.

Centralizovaný logging potrebuje collector, transport, remote storage, retention policy a query vrstvu. Journald môže byť zdrojom tejto pipeline, ale jeho lokálna dostupnosť nesmie byť zamieňaná s disaster-resistant centrálnym archívom.

## 5. Boot scope je základ korelácie

Každý boot má vlastný `_BOOT_ID`. Filter `-b` preto obmedzí query na konkrétny boot a zabráni zmiešaniu records z predchádzajúcich runtime generations.

```bash
journalctl -b
journalctl -b -1
journalctl --list-boots
```

Pri incidente po reboote je dôležité skontrolovať posledné records pred shutdownom aj prvé records nového bootu. Bez boot scope môže rovnaký PID, názov služby alebo čas vyzerať ako jeden súvislý príbeh, hoci patrí dvom odlišným systémovým stavom.

## 6. Query model cez fields a čas

```bash
journalctl -u example.service -b --since '30 minutes ago'
journalctl _PID=1234
journalctl _SYSTEMD_UNIT=nginx.service
journalctl -p warning
```

Rôzne fields sa typicky kombinujú ako AND, zatiaľ čo viac hodnôt rovnakého field-u môže vytvoriť OR skupinu. Pri zložitej query treba overiť effective match set, nie iba predpokladať SQL-like správanie.

`journalctl -o verbose` ukáže všetky fields recordu. Tento výstup je vhodný na pochopenie, ktoré metadata možno použiť na presnejší filter.

## 7. Priority je tvrdenie emitera, nie objektívny severity model

Syslog priority levels od `emerg` po `debug` pomáhajú filtrovať records, ale aplikácia ich musí klasifikovať správne. Chybná instrumentácia môže zapisovať závažný failure ako `info` alebo normálny retry ako `error`.

Priority preto nie je samostatný dôkaz dopadu. Pri incidente ju treba kombinovať s unit resultom, exit statusom, kernel events, request impactom a ďalšími signálmi.

## 8. Volatile a persistent storage

Volatile journal sa typicky nachádza v `/run/log/journal` a zanikne po reboote. Persistent journal používa `/var/log/journal` a zachováva records naprieč bootmi podľa retention policy.

```ini
[Journal]
Storage=auto
```

Pri `auto` môže existencia persistent directory ovplyvniť výsledný režim. Diagnostika preto nemá predpokladať persistence iba podľa konfigurácie; treba overiť effective config, filesystem a dostupné boots.

```bash
journalctl --list-boots
journalctl --disk-usage
```

## 9. Storage failure mení kvalitu dôkazu

Ak filesystem nemá miesto, je read-only alebo journald nedokáže vytvoriť segment, records sa nemusia uložiť podľa očakávania. Absencia logu preto nie je dôkazom absencie udalosti.

Lokálny logging musí mať vlastnú capacity a health observability. Kritický systém potrebuje alert na journal errors, disk pressure a forwarding backlog, inak môže počas incidentu stratiť práve tie evidence, ktoré sú potrebné na diagnostiku.

## 10. Retention je risk a capacity contract

Nastavenia ako `SystemMaxUse`, `SystemKeepFree`, `MaxRetentionSec` a runtime variants určujú, koľko evidence sa zachová a koľko priestoru musí zostať pre ostatný systém.

```bash
journalctl --disk-usage
sudo journalctl --vacuum-time=14d
sudo journalctl --vacuum-size=1G
```

Príliš krátka retention odstráni records pred postmortemom alebo security vyšetrovaním. Príliš veľká retention môže zaplniť `/var` a poškodiť služby, ktoré používajú rovnaký filesystem.

Retention sa preto musí odvodiť od incident review okna, compliance požiadaviek, ingest rate a dostupnej kapacity. Jednorazový vacuum nie je náhrada za stabilnú policy.

## 11. Journal files a vacuum semantics

Journal používa vlastné segmentované binary files. `journalctl --vacuum-*` odstraňuje archived segments podľa policy; nemusí okamžite zmenšiť active file, ktorý journald práve používa.

Binary journal files sa nemajú spravovať cez `logrotate`. Journald má vlastný rotation a sealing model, zatiaľ čo logrotate je určený najmä pre textové files spravované aplikáciou alebo syslog daemonom.

## 12. Rate limiting chráni host, ale zahadzuje evidence

Log storm môže spotrebovať CPU, I/O a disk rýchlejšie než systém records spracuje. Journald preto môže obmedziť burst v časovom intervale a ďalšie messages suppressnúť.

```ini
RateLimitIntervalSec=30s
RateLimitBurst=10000
```

Rate limit je ochrana availability, nie bezstratový buffer. Pri jeho aktivácii treba hľadať suppression records a uvedomiť si, že počet uložených messages nereprezentuje skutočný počet udalostí.

Správna náprava nie je automaticky vypnúť limit. Treba odstrániť log storm, agregovať opakované správy alebo presunúť high-volume telemetry do vhodnejšieho kanála.

## 13. stdout buffering a oneskorené records

Aplikácia môže bufferovať stdout inak pri termináli a inak pri pipe alebo journald descriptor. Preto sa log pri manuálnom spustení môže zobrazovať okamžite, no pod service managerom oneskorene.

Toto je user-space buffering problém pred journald ingestion. Riešením je správne flushovanie, line-buffered režim alebo logging knižnica navrhnutá pre daemon runtime, nie zmena query v `journalctl`.

## 14. Kernel logy a dmesg

`dmesg` číta aktuálny kernel ring buffer. `journalctl -k` zobrazuje kernel transport records, ktoré journald prijal a prípadne persistoval.

```bash
dmesg -T
journalctl -k -b
```

Ring buffer má obmedzenú kapacitu a staršie records sa prepíšu. Persistent journal môže zachovať kernel events dlhšie a pridať boot identity, no iba ak ich journald prijal a uložil.

Kernel records sú rozhodujúce pri OOM killeroch, filesystem errors, device resetoch, driver failures a niektorých security denials, preto sa pri systémovom incidente nemá analyzovať iba aplikačná unit.

## 15. Structured output pre automatizáciu

```bash
journalctl -o json
journalctl -o json-pretty
journalctl -o short-iso
journalctl -o cat
```

`json` zachová fields a je vhodnejší na machine processing. `cat` zobrazí iba message a odstráni kontext, preto je vhodný skôr na jednoduché ľudské čítanie než na forenznú koreláciu.

Automatizácia nemá parsovať dekorovaný human-readable output, ak existuje structured formát. Stable fields sú odolnejšie voči locale a layout zmenám.

## 16. Forwarding do syslog alebo remote collectora

Journald môže forwardovať records do syslog stacku alebo ich môže čítať samostatný collector. Konkrétny tok závisí od distribúcie a lokálnej konfigurácie.

```text
application
  ↓
journald local store
  ├── journalctl
  └── forwarding / collector
          ↓
remote log platform
```

Forwarding môže zlyhať nezávisle od lokálneho store. Preto treba monitorovať obe vrstvy: či record existuje lokálne a či bol doručený do centralizovaného systému.

## 17. At-least-once forwarding a duplicity

Collector po reconnecte môže niektoré records odoslať znova alebo pokračovať od cursoru podľa vlastného state modelu. Centralizovaný systém preto môže vidieť duplicity aj vtedy, keď journald local store obsahuje každý record iba raz.

Deduplication musí používať stabilný event identity alebo cursor semantics. Samotný timestamp a message text nemusia byť dostatočné, pretože dve legitímne udalosti môžu byť rovnaké.

## 18. Čas, monotonic clock a korelácia

Wall-clock time môže byť upravený NTP synchronizáciou alebo administrátorom. Monotonic time rastie od bootu a je spoľahlivejší na poradie udalostí v rámci jedného bootu.

Pri cross-host korelácii treba poznať timezone, NTP state a clock drift. Pri host-local analýze pomáha kombinácia `_BOOT_ID`, wall-clock timestampu a monotonic ordering.

```bash
timedatectl
journalctl -o short-monotonic -b
```

Bez synchronizovaného času môže deployment event na jednom hoste vyzerať, že nastal po chybe na inom hoste, hoci skutočné poradie bolo opačné.

## 19. Security a data minimization

Logy môžu obsahovať tokeny, session IDs, osobné údaje, request bodies, hostnames alebo stack traces. Keď sa dostanú do journald a následne do centralizovaného systému, exposure sa násobí cez storage, backups, support access a exporty.

Aplikácia má používať allowlist fields a redakciu pri zdroji. Dodatočné maskovanie v collectore je užitočné, ale nemalo by byť jedinou bariérou.

Prístup k journalu musí byť least privilege. Používateľ schopný čítať všetky system logs môže nepriamo získať citlivé prevádzkové údaje aj bez root shellu.

## 20. Diagnostika zlyhania služby

```bash
systemctl status example.service
journalctl -u example.service -b --since '15 minutes ago'
systemctl show example.service -p Result -p ExecMainCode -p ExecMainStatus
journalctl -k -b --since '15 minutes ago'
```

Postup:

1. **Urči boot a časové okno.** Bez správneho scope môžeš analyzovať starý incident alebo PID z iného bootu.
2. **Nájdi prvú kauzálnu udalosť.** Posledná chyba býva často dôsledkom skoršieho permission, dependency alebo configuration failure.
3. **Skombinuj unit state s records.** Exit status a signal vysvetľujú lifecycle, zatiaľ čo message poskytuje aplikačný kontext.
4. **Rozšír pohľad na kernel a dependencies.** OOM, storage alebo network driver failure sa nemusí objaviť v aplikačnom logu.
5. **Over completeness evidence.** Skontroluj rate limiting, storage errors, boot persistence a forwarding health.
6. **Koreluj so zmenou.** Deployment ID, artifact version alebo config revision musí byť súčasťou event contextu.

## 21. Diagnostika chýbajúcich logov

Keď očakávaný record neexistuje, postupuj po pipeline:

1. **Emitter —** zapísala aplikácia správu a flushla buffer?
2. **Descriptor alebo transport —** smeroval stdout/stderr do journalu a bol syslog socket dostupný?
3. **Journald ingestion —** nebol aktivovaný rate limit alebo service failure?
4. **Storage —** bol journal writable a mal kapacitu?
5. **Query —** nie je filter, boot alebo časové okno nesprávne?
6. **Forwarding —** existuje record lokálne, ale chýba iba v remote platforme?

Takýto postup oddeľuje „aplikácia nič nezalogovala“ od „log sa stratil alebo ho nevidím“.

## 22. Časté omyly

### „journalctl bez parametrov ukazuje iba aktuálny boot“

Nie vždy. Pri persistent store môže query zahŕňať viac bootov. Boot filter má byť pri incident analysis explicitný.

### „Keď v logu nič nie je, udalosť nenastala“

Nie. Record mohol zostať v user-space bufferi, byť suppressnutý, stratený pri storage failure alebo filtrovaný nesprávnou query.

### „systemctl status obsahuje celý log“

Nie. Zobrazuje iba obmedzený výrez a unit summary. Úplnú analýzu treba robiť cez `journalctl` a `systemctl show`.

### „journald nahrádza centralizované logovanie“

Nie. Je host-local ingestion a query vrstva. Fleet-wide retention, korelácia a disaster recovery vyžadujú remote pipeline.

### „Viac logov vždy znamená lepšiu observability“

Nie. Log storm môže znížiť signal-to-noise ratio, aktivovať rate limiting a spotrebovať kapacitu. Hodnotu prináša správny kontext, stabilné fields a akčný obsah.

## 23. Kontrolné otázky

1. Čím sa structured journal record líši od obyčajného textového riadku?
2. Aký je rozdiel medzi volatile a persistent journalom?
3. Prečo rate limiting chráni host, ale znižuje completeness evidence?
4. Ako sa líši `journalctl -k` od `dmesg`?
5. Prečo lokálny record negarantuje doručenie do centralizovaného systému?
6. Ako boot ID a monotonic time pomáhajú pri korelácii?
7. Ktoré vrstvy treba overiť, keď očakávaný log chýba?
8. Prečo sa journal files nemajú rotovať cez logrotate?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Package management](package-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Storage, mounty a filesystems →](storage-mounts-and-filesystems.md)
<!-- KNOWLEDGE-NAVIGATION:END -->