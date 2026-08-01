# Temporary Section 07 critical/high findings

> Generated from the clean Section 07 audit for manual closeout; remove before final PR.

### `docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md`

- **CRITICAL** line 73, `bare-bullet-items` — **3. Control node ako privilegovaná boundary**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `immutable execution environment digest;`, `pinned collections;`, `read-only source checkout;`, `short-lived credentials;`.
- **CRITICAL** line 129, `bare-bullet-items` — **5. Content graph: playbook, play, task, module, plugin**: 8 z 9 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `Playbook je ordered collection plays.`, `Task volá module/action alebo riadi flow.`, `Module implementuje observation a mutation unit.`, `Action plugin môže vykonať časť logiky na controlleri.`.
- **CRITICAL** line 264, `bare-bullet-items` — **10. Strategy, forks a serial**: 4 z 4 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `strategy určuje, ako hosts postupujú tasks;`, `forks obmedzuje controller concurrency;`, `serial určuje rollout batch;`, `throttle môže obmedziť konkrétnu task concurrency.`.
- **CRITICAL** line 454, `bare-bullet-items` — **18. Competing hypotheses pri mixed fleet**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `expected/resolved/recap manifests testujú H1–H3;`, `per-host vars a rendered checksum H4;`, `notifications/handler results/process start time H5;`, `LB target health/version endpoint H6;`.
- **CRITICAL** line 502, `bare-bullet-items` — **20. Acceptance a forbidden paths**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `undersized inventory;`, `staging controller credential pri production play;`, `mutable execution tag;`, `unsupported check-mode task interpretovaný ako pass;`.
- **HIGH** line 40, `list-first-introduction` — **2. Exact Ansible run subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 40, `single-sentence-concept` — **2. Exact Ansible run subject**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 326, `list-first-introduction` — **12. Handlers ako delayed state transition**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 356, `list-first-introduction` — **13. Failure a coverage model**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 356, `single-sentence-concept` — **13. Failure a coverage model**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 436, `list-first-introduction` — **17. Worked incident: delegated API task v nesprávnom účte**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 482, `bare-bullet-items` — **19. Evidence-preserving containment a recovery**: 6 z 9 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `zastaví ďalší batch;`, `identifikuje omitted, failed a mixed-state hosts;`, `odoberie unhealthy hosts z trafficu;`, `opraví inventory cache a variable contract;`.

### `docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md`

- **CRITICAL** line 83, `bare-bullet-items` — **5. State-aware module contract**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `ktoré attributes pozoruje;`, `čo znamená changed ;`, `check-mode podporu;`, `normalization;`.
- **CRITICAL** line 181, `bare-bullet-items` — **9. Deterministic artifacts**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `timestamp;`, `random value;`, `unordered serialization;`, `mutable lookup/tag;`.
- **CRITICAL** line 181, `outline-instead-of-explanation` — **9. Deterministic artifacts**: 7 odrážok je podopretých iba 10 slovami súvislého vysvetlenia.
- **CRITICAL** line 266, `bare-bullet-items` — **13. Worked failure: duplicate registration**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zachovať request/audit IDs;`, `query remote registrations podľa immutable host ID;`, `vybrať authoritative record;`, `odstrániť duplicate;`.
- **CRITICAL** line 266, `outline-instead-of-explanation` — **13. Worked failure: duplicate registration**: 6 odrážok je podopretých iba 14 slovami súvislého vysvetlenia.
- **CRITICAL** line 279, `bare-bullet-items` — **14. Partial failure a resumability**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `stable artifact/remote identities;`, `pre-validation;`, `per-step postconditions;`, `explicit partial verdict;`.
- **CRITICAL** line 374, `bare-bullet-items` — **19. Competing hypotheses pri perpetual restartoch**: 4 z 4 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `exact before/after checksums/diff H1–H4;`, `module version/current-state output H5;`, `filesystem audit H6/H7;`, `result vs actual mutation H8.`.
- **CRITICAL** line 400, `empty-section` — **20. Evidence-preserving containment a recovery**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 414, `bare-bullet-items` — **21. Acceptance a forbidden paths**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `marker pred completion;`, `mutating task s changed when: false ;`, `timestamp template;`, `duplicate POST retry;`.
- **HIGH** line 53, `list-first-introduction` — **3. Exact convergence subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 53, `single-sentence-concept` — **3. Exact convergence subject**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 71, `list-first-introduction` — **4. Fresh current-state observation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 116, `list-first-introduction` — **6. Command guards sú slabý observation model**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 155, `single-sentence-concept` — **8. Truthful result**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 181, `list-first-introduction` — **9. Deterministic artifacts**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 181, `single-sentence-concept` — **9. Deterministic artifacts**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 204, `list-first-introduction` — **10. Artifact verzus loaded runtime**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 204, `single-sentence-concept` — **10. Artifact verzus loaded runtime**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 229, `single-sentence-concept` — **11. External API idempotency**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 248, `list-first-introduction` — **12. Unknown remote outcome**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 248, `single-sentence-concept` — **12. Unknown remote outcome**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 266, `single-sentence-concept` — **13. Worked failure: duplicate registration**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 305, `list-first-introduction` — **15. Multi-writer oscillation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 305, `single-sentence-concept` — **15. Multi-writer oscillation**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 323, `list-first-introduction` — **16. Second-run acceptance**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 323, `single-sentence-concept` — **16. Second-run acceptance**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 447, `single-sentence-concept` — **„Použil som Ansible module, takže task je idempotentný“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 451, `single-sentence-concept` — **„ changed=0 znamená správny stav“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 455, `single-sentence-concept` — **„ creates dokazuje completion“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 459, `single-sentence-concept` — **„Retry je bezpečný pri timeout-e“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 463, `single-sentence-concept` — **„Dva idempotentné runy sa nebudú biť“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 181, `thin-concept-section` — **9. Deterministic artifacts**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 266, `thin-concept-section` — **13. Worked failure: duplicate registration**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.

### `docs/07-infrastructure-as-code-and-configuration-management/drift.md`

- **CRITICAL** line 7, `bare-bullet-items` — **1. Dominantný observation-to-reconciliation lifecycle**: 5 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `ktorý environment, backend, lineage a serial sa porovnávali;`, `ktorý resource address a remote ID tvoria subject;`, `ktorý writer zmenu vykonal;`, `či zmena bola autorizovaná a časovo obmedzená;`.
- **CRITICAL** line 323, `bare-bullet-items` — **12. Provider noise a signal integrity**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `server-side defaults;`, `unordered fields modelovaných ako list;`, `transient timestamps;`, `eventual consistency;`.
- **CRITICAL** line 356, `empty-section` — **13. Reconciliation decision matrix**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 397, `bare-bullet-items` — **15. Causal troubleshooting: rovnaký diff po každom apply**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `plan JSON before/after a replace paths;`, `provider debug/request IDs bez secrets;`, `cloud audit writer identity a timestamp;`, `state serial pred/po apply;`.
- **CRITICAL** line 397, `outline-instead-of-explanation` — **15. Causal troubleshooting: rovnaký diff po každom apply**: 7 odrážok je podopretých iba 30 slovami súvislého vysvetlenia.
- **HIGH** line 76, `list-first-introduction` — **3. Desired, known a actual state**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 150, `single-sentence-concept` — **Provider interpretation drift**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 154, `single-sentence-concept` — **Dependency drift**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 215, `single-sentence-concept` — **8. Worked incident: automatic revert odstránil containment**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 268, `list-first-introduction` — **10. Shared ownership a ignore changes**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 378, `single-sentence-concept` — **Compensate alebo restore**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 424, `bare-bullet-items` — **16. Authoritative recovery incidentu IAC-PAY-77**: 6 z 9 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `pozastaví scheduled auto-apply pre affected state;`, `znovu nasadí deny rule cez incident-authorized path;`, `overí traffic containment a diagnostiku;`, `aktualizuje repository alebo vykoná reviewed revert;`.
- **HIGH** line 424, `list-heavy-section` — **16. Authoritative recovery incidentu IAC-PAY-77**: 9 odrážok a iba 37 slov súvislého vysvetlenia.
- **HIGH** line 440, `bare-bullet-items` — **17. Acceptance a forbidden paths**: 2 z 4 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `unknown manual IAM expansion nesmie byť auto-adoptovaná;`, `active incident rule nesmie byť auto-revertovaná.`.
- **HIGH** line 472, `single-sentence-concept` — **„Refresh-only odstránil drift“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 476, `single-sentence-concept` — **„Exit code 0 znamená čistú produkciu“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 480, `single-sentence-concept` — **„ ignore changes vyrieši noise“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 484, `single-sentence-concept` — **„Unmanaged object je Terraform drift“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md`

- **CRITICAL** line 110, `bare-bullet-items` — **5. Unknown values a hranica plan-time rozhodovania**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `count ;`, `for each keys;`, `module instance keys;`, `provider configuration selection;`.
- **CRITICAL** line 355, `bare-bullet-items` — **14. Prečo module-wide dependency znižuje plan precision**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `čakať na celý upstream module;`, `znížiť paralelizáciu;`, `odložiť data-source reads;`, `vytvoriť viac unknown values;`.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný value-to-operation lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 162, `list-first-introduction` — **6. for each ako identity contract**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 309, `list-first-introduction` — **12. Implicitný dependency edge**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 309, `single-sentence-concept` — **12. Implicitný dependency edge**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 429, `bare-bullet-items` — **17. Cycles ako architecture signal**: 2 z 4 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `dve security objects potrebujú vzájomne computed IDs;`, `locals sa kruhovo referencujú.`.

### `docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md`

- **CRITICAL** line 421, `bare-bullet-items` — **20. Worked incident: duplicate deployment POST**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastaviť rollout controllers;`, `zachovať request IDs a API audit;`, `určiť authoritative deployment record;`, `cancel/close duplicate;`.
- **CRITICAL** line 440, `bare-bullet-items` — **21. Competing hypotheses pri files-new/process-old**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `condition inputs/types a per-item results H1–H3;`, `changed/notify events H4/H5;`, `host task timeline H6/H7;`, `active symlink/open files/process config H8;`.
- **CRITICAL** line 468, `empty-section` — **22. Evidence-preserving containment a recovery**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 482, `empty-section` — **23. Acceptance a forbidden paths**: Sekcia nemá vysvetľovací obsah.
- **HIGH** line 79, `list-first-introduction` — **4. Facts a registered results v conditions**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 99, `list-first-introduction` — **5. Loop je item inventory, nie transakcia**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 125, `list-first-introduction` — **6. Complete item preflight**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 141, `single-sentence-concept` — **7. Stable item identity**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 177, `list-first-introduction` — **9. Registered loop result**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 177, `single-sentence-concept` — **9. Registered loop result**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 207, `single-sentence-concept` — **10. Retry verzus business loop**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 257, `list-first-introduction` — **12. Handler ako queued runtime transition**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 282, `list-first-introduction` — **13. listen topic ako reusable event contract**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 337, `list-first-introduction` — **16. Complete-set staging example**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 404, `list-first-introduction` — **19. Worked incident: string boolean otvoril admin listener**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 404, `single-sentence-concept` — **19. Worked incident: string boolean otvoril admin listener**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 501, `single-sentence-concept` — **„Skipped znamená, že task nebol potrebný“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 505, `single-sentence-concept` — **„Loop je all-or-nothing“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 509, `single-sentence-concept` — **„Retry vyrieši timeout“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 513, `single-sentence-concept` — **„Handler sa spustí hneď“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md`

- **CRITICAL** line 249, `bare-bullet-items` — **9. State boundary je zároveň blast-radius boundary**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `lock a writer queue;`, `apply identity a permissions;`, `plan/recovery lifecycle;`, `dependency graph;`.
- **CRITICAL** line 270, `bare-bullet-items` — **10. Worked incident IAC-PAY-75**: 4 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `HCL bolo validné;`, `credentials boli platné;`, `plan neobsahoval destroy;`, `cloud create uspel;`.
- **HIGH** line 354, `bare-bullet-items` — **12. Authoritative recovery**: 6 z 9 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `zastaví všetky applies nad oboma candidate backend keys;`, `identifikuje orphaned VPC vytvorenú chybným runom;`, `obnoví správny backend configuration a state lineage;`, `vytvorí nový saved plan nad správnym subjectom;`.

### `docs/07-infrastructure-as-code-and-configuration-management/inventory.md`

- **CRITICAL** line 87, `bare-bullet-items` — **5. Worked failure: recyklovaná IP**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastaviť run;`, `zachovať inventory/source a SSH evidence;`, `overiť cloud instance IDs a host keys;`, `odstrániť stale static entry;`.
- **CRITICAL** line 227, `bare-bullet-items` — **10. Source order a duplicate identities**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `duplicate logical name s odlišným instance ID;`, `conflicting ansible host ;`, `conflicting environment/role;`, `unexpected variable override;`.
- **CRITICAL** line 367, `bare-bullet-items` — **16. Constructed groups a missing metadata**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `valid production metadata;`, `missing role/environment;`, `case normalization;`, `forbidden overlaps;`.
- **CRITICAL** line 426, `bare-bullet-items` — **20. Worked incident: stale cache vynechala dva hosts**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastaviť ďalší batch;`, `zachovať cache generation a source API response;`, `refreshnúť inventory cez correct account identity;`, `porovnať exact asset IDs;`.
- **CRITICAL** line 449, `bare-bullet-items` — **21. Competing hypotheses pri chýbajúcom hoste**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `direct source API vs cached output H1/H2;`, `raw metadata/filter H3;`, `--list-hosts H4;`, `resolved hostvars/instance IDs H5;`.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný source-to-coverage lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 25, `list-first-introduction` — **2. Exact inventory resolution subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 25, `single-sentence-concept` — **2. Exact inventory resolution subject**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 68, `list-first-introduction` — **4. Stable logical a immutable remote identity**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 213, `list-first-introduction` — **9. Static inventory ako vlastnená exception**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 258, `list-first-introduction` — **11. Connection variables sú execution controls**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 297, `list-first-introduction` — **13. Expected target manifest**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 367, `list-heavy-section` — **16. Constructed groups a missing metadata**: 6 odrážok a iba 55 slov súvislého vysvetlenia.
- **HIGH** line 389, `list-first-introduction` — **17. Variable conflicts v inventory**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 414, `list-first-introduction` — **19. Localhost boundary**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 426, `list-heavy-section` — **20. Worked incident: stale cache vynechala dva hosts**: 7 odrážok a iba 58 slov súvislého vysvetlenia.
- **HIGH** line 476, `single-sentence-concept` — **22. Acceptance a forbidden paths**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md`

- **CRITICAL** line 47, `empty-section` — **Remote lifecycle change**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 55, `empty-section` — **Ownership adoption**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 73, `bare-bullet-items` — **3. Replacement je identity a availability event**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `remote ID;`, `IP, DNS alebo endpoint;`, `attached policies;`, `data alebo encryption identity;`.
- **CRITICAL** line 169, `bare-bullet-items` — **6. prevent destroy ako lokálny plan guard**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `manuálnym cloud deletion;`, `compromised provider identity;`, `odstránením resource blocku spolu s rule;`, `data loss počas in-place update;`.
- **CRITICAL** line 194, `bare-bullet-items` — **7. ignore changes ako explicitný ownership handoff**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `authoritative writera;`, `dôvod delegácie;`, `acceptable bounds;`, `monitoring;`.
- **CRITICAL** line 194, `outline-instead-of-explanation` — **7. ignore changes ako explicitný ownership handoff**: 6 odrážok je podopretých iba 29 slovami súvislého vysvetlenia.
- **CRITICAL** line 322, `bare-bullet-items` — **12. CLI import verzus import block**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `je versionovaný;`, `prejde reviewom;`, `môže byť súčasťou plan/policy evidence;`, `koordinuje viac imports;`.
- **CRITICAL** line 322, `outline-instead-of-explanation` — **12. CLI import verzus import block**: 5 odrážok je podopretých iba 33 slovami súvislého vysvetlenia.
- **CRITICAL** line 340, `bare-bullet-items` — **13. Worked failure: import do nesprávneho accountu**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `freeze writers;`, `backup state;`, `overiť remote IDs, account a audit timeline;`, `odstrániť chybný binding bez mazania remote test objectu;`.
- **CRITICAL** line 428, `empty-section` — **17. moved verzus terraform state mv**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 430, `bare-bullet-items` — **moved block**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `versionovaný a reviewovateľný;`, `opakovateľný naprieč environments;`, `vhodný pre reusable module releases;`, `podporuje neskorých consumers;`.
- **CRITICAL** line 440, `bare-bullet-items` — **terraform state mv**: 4 z 4 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `okamžitá mutation jedného state subjectu;`, `vyžaduje lock a backup;`, `nie je automaticky reprodukovaná inde;`, `vhodná pre recovery alebo jednorazovú legacy migration.`.
- **HIGH** line 15, `list-first-introduction` — **1. Dominantný identity-transition lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 15, `single-sentence-concept` — **1. Dominantný identity-transition lifecycle**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 63, `list-first-introduction` — **Address refactor**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 116, `list-first-introduction` — **4. create before destroy mení poradie, nie risk model**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 116, `single-sentence-concept` — **4. create before destroy mení poradie, nie risk model**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 169, `list-heavy-section` — **6. prevent destroy ako lokálny plan guard**: 6 odrážok a iba 55 slov súvislého vysvetlenia.
- **HIGH** line 194, `list-first-introduction` — **7. ignore changes ako explicitný ownership handoff**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 226, `list-first-introduction` — **8. replace triggered by ako identity edge**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 253, `list-first-introduction` — **9. Preconditions a postconditions**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 322, `list-first-introduction` — **12. CLI import verzus import block**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 340, `list-heavy-section` — **13. Worked failure: import do nesprávneho accountu**: 7 odrážok a iba 59 slov súvislého vysvetlenia.
- **HIGH** line 363, `single-sentence-concept` — **14. Post-import plan je povinný decision point**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 386, `list-first-introduction` — **15. moved block zachováva binding pri refaktore**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 405, `list-first-introduction` — **16. Premenovanie for each keya**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 536, `single-sentence-concept` — **22. Acceptance a forbidden paths**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 555, `single-sentence-concept` — **„ create before destroy je univerzálny zero-downtime switch“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 559, `single-sentence-concept` — **„ prevent destroy je backup“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 563, `single-sentence-concept` — **„ ignore changes odstráni noise“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 567, `single-sentence-concept` — **„Import úspešne prešiel, objekt je správny“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md`

- **CRITICAL** line 126, `bare-bullet-items` — **6. Play ako target a execution policy**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `host pattern;`, `fact gathering;`, `connection/privilege;`, `strategy a batch;`.
- **CRITICAL** line 339, `bare-bullet-items` — **13. Delegation a shared API fan-out**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `host-specific idempotent member operation;`, `aggregation do jednej reviewed manifest mutation;`, `throttle alebo serializácia;`, `samostatný orchestration play;`.
- **CRITICAL** line 396, `bare-bullet-items` — **17. Competing hypotheses pri mixed runtime**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `per-host events a task path H1/H2/H5;`, `file checksum, result a notification H3/H4;`, `process start time a runtime endpoint H4/H7;`, `exact host verifier manifest H6;`.
- **CRITICAL** line 425, `bare-bullet-items` — **18. Evidence-preserving containment a recovery**: 8 z 9 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `pozastaviť ďalšie batches;`, `odstrániť unverified hosts z trafficu;`, `klasifikovať skipped, false-changed, handler-failed a partial-rescue h`, `vykonať najmenší reviewed recovery per host;`.
- **CRITICAL** line 443, `bare-bullet-items` — **19. Acceptance a forbidden paths**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `--tags config bez prerequisite;`, `false changed when pri mutation;`, `delegated staging identity;`, `handler failure po file change;`.
- **HIGH** line 48, `list-first-introduction` — **3. Task ako per-host invocation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 171, `list-first-introduction` — **7. Playbook ako orchestration medzi capabilities**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 188, `list-first-introduction` — **8. Kompletný rolling example**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 188, `single-sentence-concept` — **8. Kompletný rolling example**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 267, `list-first-introduction` — **10. Blocks, rescue a always**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 301, `list-first-introduction` — **11. Tags ako selection, nie dependency graph**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 318, `list-first-introduction` — **12. run once nie je distributed lock**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.

### `docs/07-infrastructure-as-code-and-configuration-management/modules.md`

- **CRITICAL** line 23, `bare-bullet-items` — **2. Root module verzus child module**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `backend a state subject;`, `environment composition;`, `provider configurations a credentials;`, `top-level inputs a policy;`.
- **CRITICAL** line 252, `bare-bullet-items` — **9. Module boundary podľa capability a coupling-u**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `jednu koherentnú capability;`, `jasného ownera;`, `spoločný lifecycle a release cadence;`, `testovateľný state space;`.
- **CRITICAL** line 293, `bare-bullet-items` — **11. Versioning ako compatibility promise**: 11 z 11 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `nový optional input s bezpečným defaultom;`, `nový output;`, `interný refactor s úplným moved chainom;`, `bug fix bez zmeny identity a behavior contractu.`.
- **CRITICAL** line 367, `bare-bullet-items` — **15. Upgrade lifecycle**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `moves;`, `replacements a destroys;`, `provider target changes;`, `effective default changes;`.
- **CRITICAL** line 367, `outline-instead-of-explanation` — **15. Upgrade lifecycle**: 6 odrážok je podopretých iba 4 slovami súvislého vysvetlenia.
- **CRITICAL** line 446, `bare-bullet-items` — **18. Consumer inventory**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `consumer repository/root module;`, `current module version;`, `environment a owner;`, `Terraform/provider versions;`.
- **CRITICAL** line 446, `outline-instead-of-explanation` — **18. Consumer inventory**: 7 odrážok je podopretých iba 16 slovami súvislého vysvetlenia.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný module-consumer lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 104, `single-sentence-concept` — **4. Public contract modulu**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 225, `list-first-introduction` — **8. Module composition a dependencies**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 273, `list-first-introduction` — **10. Module instance identity**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 367, `list-first-introduction` — **15. Upgrade lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 367, `single-sentence-concept` — **15. Upgrade lifecycle**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 406, `list-first-introduction` — **17. Module testing portfolio**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 446, `single-sentence-concept` — **18. Consumer inventory**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 504, `single-sentence-concept` — **21. Acceptance a forbidden paths**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 523, `single-sentence-concept` — **„Module je state boundary“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 527, `single-sentence-concept` — **„Wrapper okolo resource je automaticky abstraction“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 531, `single-sentence-concept` — **„Version number zaručuje SemVer compatibility“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 535, `single-sentence-concept` — **„Module môže konfigurovať vlastný production provider“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 539, `single-sentence-concept` — **„Môžeme odstrániť staré moved blocks po jednom release“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 367, `thin-concept-section` — **15. Upgrade lifecycle**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 446, `thin-concept-section` — **18. Consumer inventory**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.

### `docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md`

- **CRITICAL** line 7, `bare-bullet-items` — **1. Dominantný backend-to-commit lifecycle**: 3 z 4 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `Ktorý state subject čítame a zapisujeme?`, `Kto je aktuálny writer a má exkluzívne oprávnenie?`, `Ktorý snapshot je authoritative predecessor?`.
- **CRITICAL** line 109, `bare-bullet-items` — **5. Lock ako writer lease**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `backend/state subject;`, `ownera alebo run ID;`, `operation type;`, `acquisition time;`.
- **CRITICAL** line 164, `bare-bullet-items` — **8. Dvaja writers nad dvoma backendmi**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `canonical backend registry;`, `pipeline search pre staré keys/endpoints;`, `cloud audit correlation podľa writer identity;`, `inventory remote IDs naprieč states;`.
- **CRITICAL** line 390, `bare-bullet-items` — **20. Competing hypotheses pri stale locku**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `process/run inventory pre H1/H2;`, `lock owner, ID a timestamp pre H1–H3;`, `authorization audit pre H4;`, `backend telemetry pre H5/H7;`.
- **HIGH** line 109, `list-heavy-section` — **5. Lock ako writer lease**: 6 odrážok a iba 41 slov súvislého vysvetlenia.
- **HIGH** line 145, `list-first-introduction` — **7. Multi-writer race nad jedným state-om**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 190, `list-first-introduction` — **9. Force unlock neukončuje writera**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 262, `list-first-introduction` — **12. Praktický backend identity gate**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 416, `single-sentence-concept` — **21. Acceptance a forbidden paths**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 435, `single-sentence-concept` — **„Remote state automaticky znamená locking“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 443, `single-sentence-concept` — **„Force unlock je bezpečný, keď job zmizol z UI“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 447, `single-sentence-concept` — **„Migrácia skončila po úspešnom copy“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 451, `single-sentence-concept` — **„Versioning v rovnakom bucket-e je kompletný backup“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md`

- **CRITICAL** line 24, `bare-bullet-items` — **2. Kedy vzniká role boundary**: 8 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `jasný purpose a non-goals;`, `verejné inputs a defaults;`, `vlastné tasks/templates/handlers;`, `privilege, package a network dependencies;`.
- **CRITICAL** line 296, `bare-bullet-items` — **15. Supply-chain review**: 9 z 9 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `publisher/source repository;`, `release a maintenance history;`, `artifact provenance/integrity;`, `custom controller-side plugins;`.
- **CRITICAL** line 345, `bare-bullet-items` — **17. Compatibility policy**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `variable rename/type/default change;`, `new required privilege;`, `handler topic rename;`, `generated config format change;`.
- **CRITICAL** line 395, `bare-bullet-items` — **20. Competing hypotheses pri local/controller rozdiele**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `image/collection digests H1;`, `package/SBOM H2;`, `FQCN/search config H3;`, `task/handler graph H4;`.
- **CRITICAL** line 422, `bare-bullet-items` — **21. Evidence-preserving containment a recovery**: 6 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `pozastaviť rollout;`, `zachovať local aj controller images/manifests;`, `identifikovať exact collection bytes a topic/result changes;`, `obnoviť pinned known-good image alebo publikovať compatible fix;`.
- **CRITICAL** line 436, `empty-section` — **22. Acceptance a forbidden paths**: Sekcia nemá vysvetľovací obsah.
- **HIGH** line 45, `list-first-introduction` — **3. Role public contract**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 45, `single-sentence-concept` — **3. Role public contract**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 74, `list-first-introduction` — **4. Defaults verzus role vars**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 109, `list-first-introduction` — **6. Role structure ako lifecycle, nie cieľ**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 109, `single-sentence-concept` — **6. Role structure ako lifecycle, nie cieľ**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 140, `list-first-introduction` — **7. Static a dynamic role reuse**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 157, `list-first-introduction` — **8. Handler topic ako public API**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 224, `list-first-introduction` — **11. Artifact subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 243, `list-first-introduction` — **12. Requirements a pinning**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 285, `list-first-introduction` — **14. Execution environment manifest**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 318, `list-first-introduction` — **16. Role a collection test lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 318, `single-sentence-concept` — **16. Role a collection test lifecycle**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 365, `list-first-introduction` — **18. Consumer inventory**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 365, `single-sentence-concept` — **18. Consumer inventory**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 422, `list-heavy-section` — **21. Evidence-preserving containment a recovery**: 7 odrážok a iba 63 slov súvislého vysvetlenia.
- **HIGH** line 453, `single-sentence-concept` — **„Role je iba folder structure“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 457, `single-sentence-concept` — **„FQCN pinne version“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 461, `single-sentence-concept` — **„Broad range automaticky prijíma kompatibilné minor releases“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 465, `single-sentence-concept` — **„Handler topic je interný detail“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 469, `single-sentence-concept` — **„Controller image latest je pohodlná“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/terraform-practical-walkthrough.md`

- **CRITICAL** line 1013, `bare-bullet-items` — **24. Diagnostický walkthrough**: 4 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `backend config a lineage/serial testujú H1/H2;`, `Git diff a terraform state list testujú H3/H7;`, `CloudTrail/request IDs testujú H4/H5;`, `caller identity a provider debug metadata testujú H6;`.

### `docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md`

- **CRITICAL** line 366, `bare-bullet-items` — **12. Worked incident: alias sa nepreniesol**: 7 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastaviť ďalšiu replication promotion;`, `overiť, či nesprávny bucket obsahuje dáta;`, `vytvoriť explicitný alias contract;`, `zvoliť copy/import/recreate podľa data state-u;`.
- **HIGH** line 7, `bare-bullet-items` — **1. Dominantný provider-to-object lifecycle**: 5 z 7 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `Provider requirement určuje, ktorý plugin family konfigurácia používa.`, `Resource address určuje Terraform ownership identity.`, `Remote ID určuje objekt v externom systéme.`, `State binding spája Terraform address s remote ID.`.
- **HIGH** line 463, `single-sentence-concept` — **„Provider constraint stačí, lock file netreba“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md`

- **CRITICAL** line 72, `bare-bullet-items` — **3. Desired, known a actual state**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `objekt skutočne neexistuje;`, `state binding chýba;`, `načítal sa nesprávny backend/workspace;`, `address/key sa zmenila;`.
- **CRITICAL** line 146, `bare-bullet-items` — **5. Refresh mení observation model, nie desired intent**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `manuálne zmenený firewall rule;`, `objekt odstránený mimo Terraformu;`, `cloudom normalizovanú hodnotu;`, `attribute spravovaný iným controllerom;`.
- **CRITICAL** line 251, `bare-bullet-items` — **9. Evidence-preserving containment**: 7 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastav všetky pipelines nad daným backend subjectom;`, `read-only načítaj latest backend state;`, `over lineage a serial;`, `read-only queryuj remote platformu v správnom account/region context-e`.
- **CRITICAL** line 268, `bare-bullet-items` — **10. State inspection commands**: 3 z 4 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `state list preukazuje addresses v aktuálnom state subjecte.`, `output -json preukazuje root outputs v snapshot-e.`, `show zobrazuje state alebo plan podľa argumentu.`.
- **CRITICAL** line 268, `outline-instead-of-explanation` — **10. State inspection commands**: 4 odrážok je podopretých iba 31 slovami súvislého vysvetlenia.
- **CRITICAL** line 379, `bare-bullet-items` — **15. State boundaries a blast radius**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `lock;`, `writer identity;`, `plan/apply lifecycle;`, `dependency graph;`.
- **CRITICAL** line 379, `outline-instead-of-explanation` — **15. State boundaries a blast radius**: 7 odrážok je podopretých iba 30 slovami súvislého vysvetlenia.
- **CRITICAL** line 436, `bare-bullet-items` — **17. State obsahuje citlivé údaje**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `passwords a tokens;`, `private keys;`, `connection strings;`, `provider-returned sensitive attributes;`.
- **CRITICAL** line 436, `outline-instead-of-explanation` — **17. State obsahuje citlivé údaje**: 6 odrážok je podopretých iba 34 slovami súvislého vysvetlenia.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný address-to-outcome lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 7, `single-sentence-concept` — **1. Dominantný address-to-outcome lifecycle**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 251, `list-heavy-section` — **9. Evidence-preserving containment**: 8 odrážok a iba 67 slov súvislého vysvetlenia.
- **HIGH** line 268, `list-first-introduction` — **10. State inspection commands**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 294, `list-first-introduction` — **11. State mutation commands menia management model**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 306, `list-first-introduction` — **state mv**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 316, `list-first-introduction` — **state rm**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 328, `list-first-introduction` — **12. State surgery protocol**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 506, `single-sentence-concept` — **21. Authoritative recovery incidentu IAC-PAY-75**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 539, `single-sentence-concept` — **„State je cache, môžeme ho zmazať a znovu objaviť“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 543, `single-sentence-concept` — **„Failed apply nič nezmenil“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md`

- **CRITICAL** line 121, `bare-bullet-items` — **Validation**: 8 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `credentials a authorization;`, `cloud quotas a organization policy;`, `remote API behavior;`, `apply-time unknown values;`.
- **CRITICAL** line 121, `outline-instead-of-explanation` — **Validation**: 8 odrážok je podopretých iba 14 slovami súvislého vysvetlenia.
- **CRITICAL** line 290, `bare-bullet-items` — **8. Apply/integration tests**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `isolated account/project;`, `short-lived identity;`, `unique run namespace;`, `network/resource/cost limits;`.
- **CRITICAL** line 397, `bare-bullet-items` — **12. Cleanup je súčasť verdictu**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `state a remote IDs;`, `logs/request IDs;`, `ownera;`, `TTL a janitor task;`.
- **CRITICAL** line 397, `outline-instead-of-explanation` — **12. Cleanup je súčasť verdictu**: 6 odrážok je podopretých iba 27 slovami súvislého vysvetlenia.
- **CRITICAL** line 422, `bare-bullet-items` — **13. Flakiness ako explicitný failure model**: 8 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `eventual consistency;`, `API throttling;`, `shared target;`, `mutable data source;`.
- **CRITICAL** line 607, `bare-bullet-items` — **20. Competing hypotheses pri „green“ pipeline a failed production apply**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `subject manifests testujú H1/H3/H6;`, `expected evidence inventory H4;`, `policy producer/validity H5;`, `real-provider audit H2/H8;`.
- **CRITICAL** line 632, `bare-bullet-items` — **21. Authoritative recovery incidentu IAC-PAY-77**: 9 z 11 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `zastaví production apply;`, `zachová plan, test/policy reports a first-attempt logs;`, `označí verdict INVALID REPORT + MISSING UPGRADE EVIDENCE ;`, `pridá upgrade fixture 4.2.4 → 4.3.0 a moved mapping;`.
- **CRITICAL** line 650, `bare-bullet-items` — **22. Acceptance a forbidden paths**: 7 z 7 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `unencrypted production input;`, `missing upgrade mapping;`, `public IPv4 aj IPv6 exposure;`, `missing/empty policy report;`.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný risk-to-runtime evidence lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 26, `list-first-introduction` — **2. Exact Terraform evidence subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 113, `list-first-introduction` — **Formatting**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 121, `list-first-introduction` — **Validation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 156, `list-first-introduction` — **5. Invarianty priamo v Terraform contracte**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 198, `single-sentence-concept` — **6. Native Terraform tests**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 208, `list-first-introduction` — **Plan test**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 235, `list-first-introduction` — **Forbidden fixture**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 350, `list-first-introduction` — **10. Upgrade test nad existujúcim state-om**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 422, `list-heavy-section` — **13. Flakiness ako explicitný failure model**: 8 odrážok a iba 38 slov súvislého vysvetlenia.
- **HIGH** line 595, `list-first-introduction` — **19. Expected-versus-received evidence fan-in**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 632, `list-heavy-section` — **21. Authoritative recovery incidentu IAC-PAY-77**: 11 odrážok a iba 44 slov súvislého vysvetlenia.
- **HIGH** line 650, `list-heavy-section` — **22. Acceptance a forbidden paths**: 7 odrážok a iba 42 slov súvislého vysvetlenia.
- **HIGH** line 682, `single-sentence-concept` — **„ validate prešlo, infra je správna“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 686, `single-sentence-concept` — **„Mock test je zelený, provider bude fungovať“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 690, `single-sentence-concept` — **„Scanner job success znamená clean“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 694, `single-sentence-concept` — **„Assertions prešli, cleanup nie je súčasť testu“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 698, `single-sentence-concept` — **„Policy engine nefungoval, preto dočasne povoľme všetko“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 702, `single-sentence-concept` — **„Apply znovu vypočíta rovnaký plan“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 121, `thin-concept-section` — **Validation**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 397, `thin-concept-section` — **12. Cleanup je súčasť verdictu**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 607, `term-before-explanation` — **20. Competing hypotheses pri „green“ pipeline a failed production apply**: Pojmy sa objavujú najmä v odrážkach bez lokálneho vysvetlenia: `H1`, `H3`, `H6`, `H4`, `H5`, `H2`, `H8`, `H7`
- **HIGH** line 632, `term-before-explanation` — **21. Authoritative recovery incidentu IAC-PAY-77**: Pojmy sa objavujú najmä v odrážkach bez lokálneho vysvetlenia: `UPGRADE`, `EVIDENCE`, `KMS`, `DB`, `resource`

### `docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md`

- **CRITICAL** line 256, `bare-bullet-items` — **10. Readiness ako samostatný state**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `cloud-init complete;`, `host certificate ready;`, `management route functional;`, `SSH identity stable;`.
- **CRITICAL** line 295, `bare-bullet-items` — **11. Bootstrap boundary**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `trusted management identity/channel;`, `CA/host certificate;`, `minimum Python/runtime;`, `inventory registration;`.
- **CRITICAL** line 335, `empty-section` — **13. Combined pipeline**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 379, `empty-section` — **15. Failure boundaries**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 501, `bare-bullet-items` — **21. Competing hypotheses pri Terraform green / Ansible unreachable**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `remote VM lifecycle/bootstrap logs H1/H2/H8;`, `contract fields/generation H2/H3/H9;`, `inventory resolution/cache H4;`, `flow/connectivity H5/H10;`.
- **CRITICAL** line 531, `empty-section` — **22. Evidence-preserving containment a recovery**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 546, `bare-bullet-items` — **23. Acceptance a forbidden paths**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `Ansible direct mutation Terraform-owned SG rule;`, `contract with readiness != ready ;`, `empty inventory from internal state refactor;`, `runtime package latest against image-owned package;`.
- **HIGH** line 34, `list-first-introduction` — **Terraform**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 34, `single-sentence-concept` — **Terraform**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 50, `list-first-introduction` — **Ansible**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 50, `single-sentence-concept` — **Ansible**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 64, `single-sentence-concept` — **3. Ownership na úrovni objektu alebo atribútu**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 98, `single-sentence-concept` — **4. Tool selection podľa lifecycle-u**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 122, `list-first-introduction` — **5. Terraform-owned platform example**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 143, `list-first-introduction` — **6. Ansible-owned host configuration example**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 219, `list-first-introduction` — **9. Inventory generation z contractu**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 356, `list-first-introduction` — **14. Combined evidence manifest**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 356, `single-sentence-concept` — **14. Combined evidence manifest**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 381, `single-sentence-concept` — **Terraform boundary**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 385, `single-sentence-concept` — **Contract boundary**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 389, `single-sentence-concept` — **Ansible boundary**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 578, `single-sentence-concept` — **„Terraform robí infra, Ansible config — tým je boundary hotová“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 582, `single-sentence-concept` — **„Ansible môže dočasne opraviť cloud resource“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 586, `single-sentence-concept` — **„Ansible môže čítať celý Terraform state“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 590, `single-sentence-concept` — **„Terraform apply success znamená host ready“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 594, `single-sentence-concept` — **„Provisioner je jednoduchší než Ansible“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.

### `docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md`

- **CRITICAL** line 308, `bare-bullet-items` — **16. Worked failure: stale extra var smeruje do staging DB**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `odobrať hosts z trafficu;`, `zachovať job extra-var metadata a rendered files;`, `auditovať cross-environment data access;`, `odstrániť stale override;`.
- **CRITICAL** line 390, `bare-bullet-items` — **20. Competing hypotheses pri wrong endpoint na jednom hoste**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `inventory host/group output H1/H3;`, `controller job metadata H2;`, `fact timestamps H4;`, `lookup audit H5/H6;`.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný intent-to-loaded-artifact lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 25, `list-first-introduction` — **2. Exact host configuration subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 54, `single-sentence-concept` — **3. Variable contract**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 100, `list-first-introduction` — **5. Preflight validation pred side effects**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 118, `list-first-introduction` — **6. Redacted effective-value manifest**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 157, `list-first-introduction` — **8. Fact cache a freshness contract**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 194, `list-first-introduction` — **10. Registered values**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 211, `list-first-introduction` — **11. set fact a derived values**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 240, `list-first-introduction` — **13. Deterministic template rendering**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 262, `list-first-introduction` — **14. Template task a validation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 290, `list-first-introduction` — **15. Rendered artifact checksum**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 340, `list-first-introduction` — **17. Worked failure: timestamp spôsobí restart loop**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 340, `single-sentence-concept` — **17. Worked failure: timestamp spôsobí restart loop**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 372, `list-first-introduction` — **19. Loaded artifact verification**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.

### `docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md`

- **CRITICAL** line 106, `bare-bullet-items` — **4. Required values a bezpečné defaults**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `má rovnaký význam pre všetkých supported callers;`, `neoslabuje security, availability ani compliance;`, `nemení resource identity neočakávaným spôsobom;`, `je pokrytý contract testami;`.
- **CRITICAL** line 296, `bare-bullet-items` — **10. Sensitive nie je encryption ani revocation**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `že hodnota nebude v state alebo plan-e;`, `že provider ju nezaloguje;`, `že job memory/filesystem je bezpečný;`, `že terraform output -raw ju nevydá oprávnenému callerovi;`.
- **CRITICAL** line 345, `bare-bullet-items` — **11. Locals ako normalizácia, nie druhý input systém**: 5 z 5 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `canonical naming;`, `opakované expressions;`, `normalizáciu collections;`, `derived tags;`.
- **CRITICAL** line 489, `bare-bullet-items` — **16. Interface versioning**: 11 z 11 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `nový optional input s bezpečným defaultom;`, `nový output;`, `nový optional object field;`, `internú local transformáciu bez zmeny external semantics.`.
- **HIGH** line 7, `bare-bullet-items` — **1. Dominantný caller-to-consumer lifecycle**: 2 z 3 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `Input variable je explicitné API modulu.`, `Output value je publikované API smerom von.`.
- **HIGH** line 7, `list-first-introduction` — **1. Dominantný caller-to-consumer lifecycle**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 205, `list-first-introduction` — **7. Validation chráni domain invariant**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.

### `docs/07-infrastructure-as-code-and-configuration-management/vault.md`

- **CRITICAL** line 50, `bare-bullet-items` — **3. Čo Vault chráni a čo nechráni**: 9 z 9 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `controller memory;`, `temporary files;`, `rendered target files;`, `module arguments a registered results;`.
- **CRITICAL** line 115, `bare-bullet-items` — **5. Vault ID**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `environmentu;`, `ownera;`, `consumer scope-u;`, `rotation lifecycle-u;`.
- **CRITICAL** line 224, `empty-section` — **10. Target credential rotation verzus Vault rekey**: Sekcia nemá vysvetľovací obsah.
- **CRITICAL** line 249, `bare-bullet-items` — **11. Worked incident: rekey namiesto rotation**: 8 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `obmedziť access k logom;`, `auditovať použitie leaked credentialu;`, `vytvoriť nový target credential;`, `aktualizovať consumers;`.
- **CRITICAL** line 249, `outline-instead-of-explanation` — **11. Worked incident: rekey namiesto rotation**: 8 odrážok je podopretých iba 12 slovami súvislého vysvetlenia.
- **CRITICAL** line 343, `bare-bullet-items` — **17. Temporary files a cleanup**: 8 z 8 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `controller temp;`, `remote temp;`, `backup file;`, `workspace;`.
- **CRITICAL** line 343, `outline-instead-of-explanation` — **17. Temporary files a cleanup**: 8 odrážok je podopretých iba 11 slovami súvislého vysvetlenia.
- **CRITICAL** line 383, `bare-bullet-items` — **19. Competing hypotheses pri partial fleet rotation**: 6 z 6 odrážok iba pomenúva položky bez kontextového vysvetlenia. Príklady: `expected/resolved hosts H1;`, `Vault run metadata H2;`, `effective epoch manifest H3;`, `checksum/handler/process start H4/H5/H8;`.
- **CRITICAL** line 383, `outline-instead-of-explanation` — **19. Competing hypotheses pri partial fleet rotation**: 6 odrážok je podopretých iba 1 slovami súvislého vysvetlenia.
- **CRITICAL** line 421, `empty-section` — **21. Acceptance a forbidden paths**: Sekcia nemá vysvetľovací obsah.
- **HIGH** line 24, `list-first-introduction` — **2. Exact secret subject**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 24, `single-sentence-concept` — **2. Exact secret subject**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 175, `list-first-introduction` — **8. Plaintext path**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 226, `list-first-introduction` — **Vault rekey**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 226, `single-sentence-concept` — **Vault rekey**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 237, `list-first-introduction` — **Target credential rotation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 237, `single-sentence-concept` — **Target credential rotation**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 271, `list-first-introduction` — **12. Consumer rollout**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 287, `list-first-introduction` — **13. Runtime verification**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 302, `single-sentence-concept` — **14. Old credential revocation**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 343, `single-sentence-concept` — **17. Temporary files a cleanup**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 383, `list-first-introduction` — **19. Competing hypotheses pri partial fleet rotation**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 383, `single-sentence-concept` — **19. Competing hypotheses pri partial fleet rotation**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 405, `list-first-introduction` — **20. Evidence-preserving containment a recovery**: Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.
- **HIGH** line 405, `single-sentence-concept` — **20. Evidence-preserving containment a recovery**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 439, `single-sentence-concept` — **„Vault vyriešil secrets management“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 443, `single-sentence-concept` — **„Rekey je rotation“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 447, `single-sentence-concept` — **„ no log zabráni všetkým leakom“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 451, `single-sentence-concept` — **„Nový secret funguje, môžeme skončiť“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 455, `single-sentence-concept` — **„Vault password môže byť v image“**: Bežná konceptuálna sekcia má iba jednu vysvetľovaciu vetu. Musí obsahovať viacvetový výklad významu, mechanizmu alebo dôsledku.
- **HIGH** line 249, `thin-concept-section` — **11. Worked incident: rekey namiesto rotation**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 343, `thin-concept-section` — **17. Temporary files a cleanup**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.
- **HIGH** line 383, `term-before-explanation` — **19. Competing hypotheses pri partial fleet rotation**: Pojmy sa objavujú najmä v odrážkach bez lokálneho vysvetlenia: `H1`, `H2`, `H3`, `H4`, `H5`, `H8`, `H6`, `H7`
- **HIGH** line 383, `thin-concept-section` — **19. Competing hypotheses pri partial fleet rotation**: Konceptuálna sekcia má menej než 28 slov súvislého výkladu.

### `docs/07-infrastructure-as-code-and-configuration-management/ansible-practical-walkthrough.md`

- **HIGH** line 996, `bare-bullet-items` — **28. Diagnostický walkthrough pri mixed fleet**: 4 z 6 odrážok nemá vysvetlenú úlohu, význam alebo dôsledok v aktuálnom kontexte. Príklady: `expected/resolved/attempted manifests testujú H1–H3;`, `callback/handler result a systemd start time testujú H5;`, `LB member inventory a backend identity testujú H7;`, `direct per-host request a timestamps testujú H8.`.
