# SELinux a AppArmor

SELinux a AppArmor sú Linux Security Modules poskytujúce Mandatory Access Control nad rámec klasického DAC. Kernel najprv vyhodnotí bežné identity a permissions a následne LSM policy pre subject, object, operation a context. Root alebo capability preto nemusia obísť MAC denial.

SELinux používa labels a type-enforcement rules; AppArmor primárne viaže profile na executable a path-oriented access. Obe platformy majú policy generation, loaded kernel state, enforcement mode a audit evidence. Súbor s opravenými Unix mode bits môže byť stále blokovaný nesprávnym SELinux type-om alebo AppArmor profile transitionom.

Bezpečný troubleshooting zachová denial evidence, identifikuje exact process/object/action a opraví label, transition alebo policy pri správnej boundary. Vypnutie enforcementu alebo broad allow rule iba potvrdí, že MAC vrstva mala vplyv; nepreukazuje správnu least-privilege nápravu. Acceptance testuje pôvodný povolený flow aj zakázaný susedný flow po reload/restart generation.

## 1. Definícia

SELinux a AppArmor sú Linux Security Modules, ktoré implementujú Mandatory Access Control — MAC. Kernel nimi vynucuje systémovú politiku nezávislú od toho, čo povoľujú owner, group, mode bits alebo POSIX ACL.

Discretionary Access Control — DAC — umožňuje vlastníkovi alebo privilegovanému procesu meniť veľkú časť oprávnení objektu. MAC pridáva pravidlá, ktoré môže zmeniť iba správca politiky a ktoré platia aj pre kompromitovaný proces s legitímnym UID.

```text
syscall
  ↓
namespace a pathname/object resolution
  ↓
DAC a ACL
  ↓
capability checks
  ↓
SELinux alebo AppArmor policy
  ↓
mount, seccomp a subsystem-specific policy
  ↓
operation alebo denial
```

Operácia musí prejsť všetkými povinnými vrstvami. `chmod 777` preto nevyrieši SELinux alebo AppArmor denial a zároveň zbytočne oslabí DAC.

## 2. Threat model

MAC obmedzuje, čo môže proces vykonať po kompromitácii. Web server môže mať DAC právo čítať viac súborov pod spoločným service accountom, ale MAC policy mu dovolí iba web content a zakáže SSH keys, databázové secrets alebo zápis do systémovej konfigurácie.

```text
compromised httpd process
  ├── môže čítať označený web content
  ├── môže zapisovať iba do určeného runtime pathu
  ├── nemôže čítať user SSH keys
  └── nemôže otvoriť ľubovoľný outbound socket bez policy
```

MAC nie je ochrana pred všetkým. Kernel vulnerability, príliš široká policy, privileged container alebo writable executable môže boundary oslabiť.

## 3. DAC verzus MAC

DAC rozhoduje primárne podľa UID/GID, mode bits a ACL. Root alebo capability ako `CAP_DAC_OVERRIDE` môže veľkú časť DAC checks obísť.

MAC rozhoduje podľa security labelov alebo profilov a povahy operácie. Root proces môže byť stále zamietnutý, ak jeho SELinux domain alebo AppArmor profile nemá požadované pravidlo.

```text
DAC allow + MAC deny = deny
DAC deny  + MAC allow = deny
DAC allow + MAC allow = operácia pokračuje k ďalším kontrolám
```

Pri diagnostike treba najprv zistiť, ktorá vrstva zamietla operáciu. Náhodné zmeny DAC môžu zamaskovať pôvodný problém a vytvoriť nový bezpečnostný incident.

## 4. Linux Security Modules

LSM je kernel framework pre security hooks v objektoch a operáciách, napríklad file open, inode permission, process transition, socket create alebo mount. SELinux a AppArmor používajú tieto hooks na policy decision.

LSM nefunguje ako externý antivirus po vykonaní operácie. Decision prebieha v kernelovej ceste pred povolením chráneného action.

Moderný kernel môže podporovať stacking niektorých LSMs, ale distribúcia typicky používa jeden hlavný MAC systém. Aktívny stav treba overiť na konkrétnom hoste, nie predpokladať podľa názvu distribúcie.

## 5. SELinux security context

SELinux priraďuje subjects a objects security context. Typický context:

```text
system_u:system_r:httpd_t:s0
```

Časti:

- **SELinux user** — policy identity odlišná od Unix username.
- **Role** — používa sa pri role-based transitions, najmä pre používateľské sessions.
- **Type/domain** — najdôležitejšia časť bežného serverového Type Enforcement modelu.
- **MLS/MCS level alebo range** — bezpečnostné levely a categories používané napríklad pri kontajnerovej izolácii.

Procesný type sa často nazýva domain. Súbor, socket alebo port má target type a policy rozhoduje, či source domain smie vykonať konkrétnu permission nad object class.

## 6. SELinux Type Enforcement

Zjednodušené policy pravidlo:

```text
allow httpd_t httpd_sys_content_t:file { open read getattr map };
```

Rozhodnutie používa:

```text
source context: httpd_t
target context: httpd_sys_content_t
object class:   file
permission:     read
```

Pathname nie je primárna security identity. Kernel po pathname resolution pracuje s labelom inode alebo iného objektu.

Dva súbory s rovnakým názvom v rôznych adresároch môžu mať rovnaký type a dostať rovnakú policy. Naopak, súbor presunutý na netypický path si môže zachovať nevhodný label a správať sa odlišne od susedných súborov.

## 7. SELinux režimy

```bash
getenforce
sestatus
```

- **Enforcing** — policy denials sa blokujú a auditujú.
- **Permissive** — policy vypočíta denial a audituje ho, ale operáciu globálne nezablokuje.
- **Disabled** — SELinux hooks a labeling model nie sú aktívne v normálnom enforcement režime.

Permissive je diagnostický režim, nie oprava. Globálny permissive mení failure model celého hosta a môže skryť útok alebo inú súbežnú chybu.

Bezpečnejšie je použiť per-domain permissive iba pre skúmanú domain, ak to nástroje a policy podporujú. Aj vtedy treba experiment časovo obmedziť a audit logy vyhodnotiť.

## 8. Aktuálny label a očakávaný label

Aktuálny file label je typicky uložený v extended attribute `security.selinux`. Očakávaný label vychádza z file-context rules distribuovanej alebo lokálnej policy.

Zobrazenie:

```bash
ls -Zd /srv/site /srv/site/index.html
ps -eZ | grep httpd
id -Z
```

Dočasná zmena:

```bash
sudo chcon -t httpd_sys_content_t /srv/site/index.html
```

`chcon` mení aktuálny label, ale nevytvára trvalé path-to-label pravidlo. `restorecon` alebo full relabel ho môže prepísať.

## 9. Trvalé file-context mapping

Netypický aplikačný path treba pridať do lokálnej file-context policy:

```bash
sudo semanage fcontext -a \
  -t httpd_sys_content_t \
  '/srv/site(/.*)?'

sudo restorecon -Rv /srv/site
```

Mentálny model:

```text
semanage fcontext
  → desired path-label mapping

restorecon
  → reconciliation aktuálneho inode labelu s mappingom
```

Tento model je reprodukovateľný a prežije relabel. Samotné `chcon` je vhodné na krátky diagnostický test, nie ako finálna konfigurácia.

## 10. Copy, move a label inheritance

Nový súbor typicky dostane label podľa parent directory a policy transition rules. Presun na tom istom filesysteme však často mení iba directory entry a inode si zachová pôvodný label.

To vytvára častý incident:

```text
súbor vytvorený v /tmp s tmp_t
  ↓ mv na /var/www/html
inode si zachová tmp_t
  ↓
httpd_t dostane denial
```

Copy vytvorí nový inode a môže dostať label cieľového directory. Move a copy preto nemajú rovnakú label semantics.

Po presune contentu do spravovaného pathu je vhodné použiť `restorecon`, nie ručne hádať type.

## 11. SELinux process transitions

Executable file type a policy môžu pri `execve()` spôsobiť prechod procesu do novej domain. Service spustená z označeného executable tak nemusí zostať v domain launcheru.

```text
init_t / systemd
  + executable type httpd_exec_t
  + domain transition policy
  → httpd_t
```

Ak executable dostane nesprávny label, proces môže zostať v neočakávanej domain alebo execution zlyhá. Kontrola iba `User=` v systemd unit preto nevysvetľuje celý security context.

Procesný context treba overiť po štarte:

```bash
ps -eZ | grep <process>
cat /proc/<pid>/attr/current
```

## 12. SELinux object classes

SELinux nerozhoduje iba nad files. Policy rozlišuje object classes a permissions, napríklad:

- file, dir, symlink a filesystem,
- process a capability,
- TCP/UDP socket a node,
- network port,
- message queue alebo shared memory,
- service-specific kernel objects.

Permission `name_connect` nad `tcp_socket` nie je to isté ako file `read`. Pri denial logu treba čítať `tclass` a denied permission, nie iba pathname.

Network denial nemusí mať target file. Môže sa týkať port type, remote node alebo socket class.

## 13. SELinux port labels

SELinux môže priraďovať types aj TCP/UDP portom. Web server domain preto nemusí bindnúť ľubovoľný port, hoci má Unix capability a port je voľný.

```bash
sudo semanage port -l | grep http_port_t
```

Pridanie podporovaného alternatívneho portu:

```bash
sudo semanage port -a -t http_port_t -p tcp 8088
```

Port labeling dopĺňa network firewall. Firewall rozhoduje o packet flow; SELinux rozhoduje, ktorá domain môže daný port bindnúť alebo používať podľa policy.

## 14. SELinux booleans

Booleans zapínajú vopred pripravené voliteľné vetvy policy. Umožňujú podporiť bežný variant bez tvorby vlastného modulu.

```bash
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on
```

`-P` zapíše persistent policy stav a môže trvať dlhšie pre rebuild policy store.

Boolean môže byť širší než konkrétny incident. `httpd_can_network_connect` nepovoľuje iba jeden hostname; povoľuje definovanú kategóriu network connect správania pre domain.

Pred zapnutím treba:

- prečítať význam booleanu,
- potvrdiť legitímnu aplikačnú potrebu,
- porovnať užšiu alternatívu,
- zapísať rozhodnutie do source of truth.

## 15. SELinux policy modules

Custom policy module je vhodný, keď aplikácia legitímne potrebuje správanie, ktoré distribučná policy nepokrýva a ktoré nemožno vyriešiť správnym labelom alebo booleanom.

Module má byť úzky:

- konkrétna source domain,
- konkrétny target type,
- konkrétna object class,
- minimálne permissions,
- verziovaný source a build process,
- test v enforcing režime.

Široké pravidlá typu „allow domain všetko nad unconfined object“ ničia MAC boundary. Policy code sa má reviewovať podobne ako firewall alebo IAM policy.

## 16. AVC audit evidence

SELinux denial sa typicky zaznamená ako AVC — Access Vector Cache — event.

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
sudo journalctl --since '10 minutes ago' | grep -i avc
```

Dôležité fields:

- **`scontext`** — source process context.
- **`tcontext`** — target object context.
- **`tclass`** — object class.
- **Denied permission** — presná operácia, napríklad `read`, `write`, `name_connect` alebo `execute`.
- **Process metadata** — command, PID a executable.
- **Target metadata** — pathname, inode, port alebo ďalšia identita.

Audit event treba korelovať s časom reprodukcie. Starý denial inej domain nie je dôkaz root cause aktuálneho incidentu.

## 17. Bezpečný SELinux troubleshooting

Odporúčaný postup:

1. **Reprodukuj jednu konkrétnu operáciu** — minimalizuj šum v audit logoch.
2. **Potvrď syscall a errno** — odlíš LSM denial od aplikačnej validácie.
3. **Nájdi zodpovedajúci AVC** — rovnaký čas, process a target.
4. **Over source domain** — proces môže bežať mimo očakávaného transitionu.
5. **Over target label** — porovnaj `ls -Z` a `matchpathcon`.
6. **Over podporovaný boolean alebo port type** — preferuj existujúcu policy vetvu.
7. **Oprav desired label mapping** — `semanage fcontext` a `restorecon`.
8. **Custom module vytvor až po threat analýze** — denial môže odhaľovať exploit alebo chybný design.
9. **Testuj v enforcing režime** — permissive test nepotvrdzuje, že neexistujú ďalšie denials.

## 18. `audit2allow` a jeho riziko

`audit2allow` preloží denial events na syntakticky možné allow rules. Nevie rozhodnúť, či bola operácia legitímna.

Nebezpečný tok:

```text
všetky AVC events
  ↓ audit2allow
široký custom module
  ↓
trvalé povolenie chýb, útokov a nesúvisiacich operácií
```

Nástroj je vhodný ako analytická pomôcka po root-cause potvrdení. Výstup treba minimalizovať, reviewovať po jednotlivých object classes a porovnať s distribučnými interfaces.

`audit2why` alebo troubleshooting tooling môže vysvetliť policy context, ale tiež nenahrádza security rozhodnutie.

## 19. AppArmor mentálny model

AppArmor priraďuje procesom profily a policy typicky vyjadruje povolené path operácie, capabilities, network family/protocol a execute transitions.

```text
executable alebo attachment condition
  ↓
AppArmor profile
  ↓
file/network/capability/exec rules
  ↓
allow alebo deny
```

AppArmor sa často označuje ako path-based. Kernel však pracuje s resolved objek­tmi, mount namespaces a mediation state, takže model nie je iba textový regex nad pathname.

Path aliases, bind mounts, hard links a namespace views môžu meniť, ktorý rule sa použije. Profil treba testovať v reálnom deployment filesystem layout-e.

## 20. AppArmor profile modes

```bash
sudo aa-status
```

- **Enforce** — profile pravidlá sa blokujú a audituje sa violation.
- **Complain** — porušenia sa auditu­jú, ale väčšina sa nevynúti.
- **Unconfined alebo unloaded** — proces nemá príslušný loaded profile.

Complain mode je vhodný na učenie workloadu a generovanie návrhov. Nie je bezpečný finálny stav pre službu, ktorá má byť confined.

Profil môže byť v enforce režime, ale proces pod ním nemusí bežať, ak attachment alebo execute transition neprebehli. Stav profilu a runtime confinement sú dve odlišné otázky.

## 21. AppArmor profile anatomy

Zjednodušený profil:

```text
#include <tunables/global>

/usr/local/bin/example {
  #include <abstractions/base>

  /usr/local/bin/example mr,
  /etc/example/** r,
  /var/lib/example/** rwk,
  /var/log/example/** rw,

  network inet stream,
  capability net_bind_service,

  deny /home/** rwklx,
}
```

Pravidlá rozlišujú operácie:

- **`r`** — čítanie dát alebo metadata podľa pravidla.
- **`w`** — zápis.
- **`m`** — memory map s executable alebo ďalšími relevantnými flags.
- **`k`** — file locking.
- **`l`** — link operation.
- **`x` varianty** — execute a profile transition semantics.

Široký glob ako `/** rw` ničí confinement podobne ako široký SELinux allow rule.

## 22. AppArmor execute transitions

Spustenie child executable môže:

- zostať v current profile,
- prejsť do named child profile,
- použiť profile attached k executable,
- bežať unconfined podľa konkrétneho execute rule.

Execute mode je bezpečnostne kritický. Program môže mať úzky filesystem access, ale spustiť shell alebo helper s voľnejším profilom.

Transitívny execution graph treba auditovať:

```text
main service
  → shell wrapper
  → helper
  → interpreter
  → plugin
```

Každý prechod musí mať zámerný profile behavior.

## 23. AppArmor abstractions a tunables

Abstractions sú zdieľané rule fragments pre bežné potreby, napríklad DNS resolver alebo base libraries. Znižujú duplicitu, ale môžu povoliť viac paths než konkrétna aplikácia potrebuje.

Tunables umožňujú environment-specific path definitions. Uľahčujú portabilitu profilov, ale výsledný expanded profile treba stále reviewovať.

Include nie je iba dokumentačný import. Rozširuje efektívne povolenia profilu a zmena distribučnej abstraction môže zmeniť behavior viacerých services.

## 24. AppArmor tooling a logs

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.example
sudo aa-status
sudo aa-logprof
sudo aa-genprof /usr/local/bin/example
```

Audit events:

```bash
journalctl -k | grep -i apparmor
journalctl | grep 'apparmor="DENIED"'
```

Dôležité fields:

- **Profile** — confinement identity procesu.
- **Operation** — file open, capability, network, mount alebo exec transition.
- **Requested a denied mask** — požadované a zamietnuté permissions.
- **Name/path** — objekt v aktuálnom namespace view.
- **Process metadata** — PID, command a parent.

`aa-logprof` môže navrhnúť pravidlo, ale nevie rozhodnúť, či workload nemal vykonávať nebezpečnú operáciu.

## 25. Bezpečný AppArmor troubleshooting

1. **Potvrď, že proces má očakávaný profil** — loaded profile nestačí.
2. **Reprodukuj konkrétny denial** — oddelíš incident od historického šumu.
3. **Čítaj operation a denied mask** — path sám nestačí.
4. **Over mount namespace a resolved path** — kontajner môže mať iný filesystem view.
5. **Over execute transition chain** — denial môže pochádzať z helper profilu.
6. **Použi complain iba dočasne a čo najužšie** — zachovaj audit evidence.
7. **Reviewuj návrh `aa-logprof`** — nepovoľuj celý directory tree pre jednu missing file.
8. **Reloadni profil a testuj v enforce režime** — vrátane negatívnych testov.

## 26. SELinux verzus AppArmor

| Vlastnosť | SELinux | AppArmor |
|---|---|---|
| Primárna identita | labels a security contexts | profile attachment a path-oriented rules |
| Hlavný policy model | Type Enforcement, role/MLS/MCS vrstvy | per-program profiles a execute transitions |
| File policy | inode/object label | resolved path a profile rule |
| Bežná flexibilita | file contexts, booleans, policy modules | abstractions, tunables, child profiles |
| Audit evidence | AVC records so source/target contexts | profile, operation, path a masks |
| Prevádzková sila | nezávislosť od pathname po labeling | ľahšie čitateľný path-centric profil pre mnohé use cases |
| Prevádzkové riziko | nesprávne labels alebo príliš široký module | path aliases/mounty a príliš široké globs/transitions |

Jeden systém nie je univerzálne lepší. Dôležitá je distribučná integrácia, kvalita dostupných policies, workload model a schopnosť tímu správne udržiavať a diagnostikovať enforcement.

## 27. Kontajnery a SELinux

Kontajnerový proces môže bežať v spoločnom container domain type, ale dostať odlišné MCS categories. Categories bránia, aby dva kontajnery s rovnakým všeobecným type čítali navzájom označené dáta.

```text
container A: container_t:s0:c1,c2
container B: container_t:s0:c3,c4
```

Bind mount musí mať label kompatibilný s container domain a sharing modelom. Runtime voľby typu `:z` a `:Z` môžu meniť labels:

- **Shared relabel** — path môže používať viac kontajnerov.
- **Private relabel** — path dostane label pre jeden izolovaný workload.

Použitie naslepo môže relabelovať hostový directory a narušiť inú službu. Produkčný volume labeling má byť súčasťou storage a security designu.

## 28. Kontajnery a AppArmor

Kontajner runtime môže priradiť profile procesu pri štarte. Profil môže obmedziť mount, capabilities, file paths a network behavior aj vtedy, keď je kontajnerový UID root.

Path rules sa vyhodnocujú vo filesystem view procesu. Profil preto musí zohľadňovať image layout, bind mounts a runtime-generated paths.

Default runtime profile je defense-in-depth baseline, nie workload-specific least privilege. Citlivá aplikácia potrebuje vlastný profil a negatívne testy.

## 29. Kubernetes integration

Kubernetes security context môže vyberať SELinux options alebo AppArmor profile. Exact fields a support závisia od verzie clusteru, node OS a runtime.

Policy musí byť dostupná na node, kde Pod pristane. Manifest odkazujúci na neexistujúci profil môže viesť k odmietnutiu alebo inému runtime behavior podľa integrácie.

Pri incidentnej diagnostike treba korelovať:

- Pod security context,
- node runtime config,
- process context/profile na konkrétnom node,
- volume labels a mount options,
- audit events host kernelu.

Cluster-level YAML sám nie je dôkaz efektívnej hostovej policy.

## 30. Systemd a MAC

Systemd vie explicitne nastaviť SELinux context alebo AppArmor profile pre service, ale bežnejšie sa používa policy-driven executable transition a distribučná integrácia.

Relevantné unit properties môžu zahŕňať:

```ini
[Service]
SELinuxContext=system_u:system_r:example_t:s0
AppArmorProfile=example-profile
```

Dostupnosť a vhodnosť závisia od systemd a platformy. Nesprávne explicitné context nastavenie môže obísť očakávaný domain transition alebo zlyhať pred spustením aplikácie.

Systemd sandboxing a MAC sa dopĺňajú. `ProtectSystem=strict` zmení mount view, zatiaľ čo SELinux/AppArmor rozhoduje o object access; obidve vrstvy môžu nezávisle zamietnuť tú istú operáciu.

## 31. Policy maintenance lifecycle

MAC policy nie je jednorazový súbor. Mení sa spolu s executable paths, dependencies, deployment layoutom a workload behavior.

Bezpečný lifecycle:

1. **Definuj očakávané správanie** — files, network endpoints, capabilities a child processes.
2. **Použi distribučnú policy alebo abstraction** — znižuje custom maintenance.
3. **Pridaj lokálne mappingy alebo úzke pravidlá** — verziované v source of truth.
4. **Testuj pozitívne use cases** — legitímna prevádzka musí fungovať v enforce režime.
5. **Testuj negatívne use cases** — zakázaný path alebo operation musí zostať blokovaný.
6. **Monitoruj denials po deploymente** — nový code path môže odhaliť chýbajúcu policy alebo regresiu.
7. **Odstraňuj zastarané pravidlá** — policy iba rastúca o nové allow rules postupne stráca hodnotu.

## 32. Časté omyly

### „Keď mode bits povoľujú prístup, kernel ho musí povoliť“

MAC, read-only mount, capabilities a ďalšie vrstvy môžu operáciu stále zamietnuť.

### „Root obíde SELinux alebo AppArmor“

Root môže meniť policy iba s príslušnou authority, ale bežná operácia root procesu je stále subject MAC enforcementu.

### „`setenforce 0` je oprava“

Je to globálny diagnostický experiment, ktorý vypína enforcement pre celý host. Root cause a bezpečná policy zostávajú nevyriešené.

### „`chcon` je trvalá SELinux konfigurácia“

Mení aktuálny label inode. `restorecon` alebo relabel ho môže vrátiť podľa file-context mappingu.

### „Každý AVC denial treba povoliť“

Denial môže znamenať exploit attempt, chybný path, zlý domain transition alebo zbytočnú aplikačnú operáciu.

### „Complain mode znamená, že profil je hotový“

Complain iba loguje väčšinu porušení. Finálna policy musí fungovať a byť testovaná v enforce režime.

### „AppArmor profil je iba zoznam paths“

Obsahuje operation masks, capabilities, network rules a execute transitions; mount namespace a aliases ovplyvňujú resolved objekty.

### „Container label/profile nahrádza ostatné kontroly“

Kontajner stále potrebuje bezpečné capabilities, seccomp, user mapping, mounts a runtime policy.

## 33. Troubleshooting: služba nevie čítať nový data path

1. **Potvrď syscall a pathname** — `strace` alebo aplikačný log.
2. **Over DAC/ACL a traversal** — MAC denial nemusí byť jediná chyba.
3. **Zisti process context/profile** — runtime stav, nie iba config file.
4. **Zisti target label alebo resolved AppArmor path** — porovnaj s očakávaným deployment layoutom.
5. **Nájdi audit event v rovnakom čase** — source, target, class a operation.
6. **SELinux: porovnaj `matchpathcon` a `restorecon`** — netypický path potrebuje `semanage fcontext`.
7. **AppArmor: over include, glob a execute transition** — helper môže mať iný profil.
8. **Testuj úzku opravu v enforce režime** — nepovoľuj širší directory tree, než workload potrebuje.

## 34. Troubleshooting: aplikácia funguje iba po vypnutí MAC

Tento výsledok potvrdzuje involvement policy layer, ale neurčuje správnu opravu.

1. Reprodukuj denial s enforcementom zapnutým.
2. Získaj presný audit record.
3. Over, či aplikácia beží v správnej domain/profile.
4. Over, či target object má správny label/path a či nebol presunutý z temporary directory.
5. Skontroluj podporovaný boolean, port type alebo abstraction.
6. Preskúmaj, či požadovaná operácia patrí do legitímneho threat modelu aplikácie.
7. Vytvor minimálnu policy zmenu a negatívny test.
8. Odstráň diagnostický permissive/complain stav.

## 35. Kontrolné otázky

1. Aký je rozdiel medzi DAC a MAC?
2. Prečo môže root proces dostať SELinux/AppArmor denial?
3. Z akých častí sa skladá SELinux security context?
4. Prečo je type/domain najdôležitejší v bežnom Type Enforcement modeli?
5. Aký je rozdiel medzi `chcon` a `semanage fcontext` plus `restorecon`?
6. Prečo môže `mv` zachovať nesprávny SELinux label?
7. Čo znamenajú `scontext`, `tcontext`, `tclass` a denied permission v AVC evente?
8. Prečo boolean môže byť širší než konkrétny incident?
9. Prečo sa `audit2allow` nesmie používať bez security review?
10. Ako AppArmor execute transitions ovplyvňujú child proces?
11. Prečo loaded AppArmor profile nedokazuje, že ním je proces confined?
12. Ako sa MAC dopĺňa so systemd sandboxingom a kontajnerovými controls?

## 36. Zhrnutie

SELinux a AppArmor pridávajú kernelom vynucovanú Mandatory Access Control policy nad UID/GID, mode bits, ACL a capabilities. SELinux používa security contexts a Type Enforcement; AppArmor používa programové profily s path, operation, capability, network a execute-transition pravidlami.

Bezpečný troubleshooting začína presným audit eventom, process security identity a target object state. Oprava má používať správny label mapping, existujúci boolean/profile abstraction alebo minimálnu verziovanú policy; globálny permissive režim a automatické povoľovanie denialov iba odstraňujú ochranu bez vyriešenia root cause.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Linux capabilities](linux-capabilities.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Performance a troubleshooting →](performance-and-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
