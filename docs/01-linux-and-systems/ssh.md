# SSH

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Linux networking](linux-networking.md), [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
- Súvisiace témy: public-key cryptography, bastion hosts, port forwarding, automation, secrets management

## 1. Mentálny model

SSH vytvára šifrovaný transport medzi klientom a serverom, overí identitu servera, následne overí používateľa a až potom otvorí jeden alebo viac logických channels. Bezpečnosť preto nestojí iba na private key; závisí aj od host identity, server policy, client configuration a povolených channel capabilities.

```text
TCP connection
  ↓
Algorithm negotiation a key exchange
  ↓
Server host-key verification
  ↓
Encrypted transport
  ↓
User authentication
  ↓
Session / command / SFTP / forwarding channels
```

Ak sa zlyhanie diagnostikuje iba ako „SSH nejde“, miešajú sa DNS, TCP, host trust, user authentication a remote command execution. Každá vrstva má vlastné dôkazy a vlastný failure model.

## 2. Transport layer

Klient a server najprv vyjednajú key-exchange, host-key, cipher a integrity algoritmy. Key exchange vytvorí session keys, ktorými sa následná komunikácia šifruje a chráni proti modifikácii.

Host private key nepoužíva server na šifrovanie celej session. Slúži na podpis transportného handshakeu, aby klient vedel, že komunikuje s očakávaným serverom a nie s útočníkom na trase.

```bash
ssh -vv host
ssh -Q kex
ssh -Q key
ssh -Q cipher
```

Algorithm mismatch môže zablokovať spojenie ešte pred user authentication. Správna náprava je aktualizovať klienta/server alebo explicitne riadiť policy; plošné povolenie starých algoritmov zväčšuje attack surface.

## 3. Host keys a server identity

OpenSSH server drží host private keys typicky v `/etc/ssh/ssh_host_*_key`. Klient si očakávaný public key alebo certifikačnú autoritu uchováva v `known_hosts`.

```text
Server host private key
  ↓ podpis handshakeu
Client
  ↓ porovná public identity s trusted recordom
Host accepted alebo rejected
```

Pri prvom spojení fingerprint treba overiť cez nezávislý dôveryhodný kanál, napríklad provisioning inventory, cloud console alebo host CA. Samotné zobrazenie fingerprintu v rovnakom sieťovom spojení nedokazuje jeho správnosť.

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
ssh-keygen -F server.example
```

Varovanie `REMOTE HOST IDENTIFICATION HAS CHANGED` môže znamenať legitímnu reinštaláciu, presmerovanie DNS alebo MITM útok. Záznam sa nemá vymazať automaticky; najprv treba potvrdiť novú identitu a dôvod zmeny.

## 4. `known_hosts` a trust policy

`known_hosts` mapuje hostname alebo address na očakávaný host key. Záznam môže byť hashovaný, viazaný na viac mien alebo nahradený dôverou v SSH host certificate authority.

```sshconfig
Host *.corp.example
    UserKnownHostsFile ~/.ssh/known_hosts
    StrictHostKeyChecking yes
```

`StrictHostKeyChecking=no` odstraňuje kritickú MITM ochranu. V automatizácii je lepšie distribuovať trusted host keys alebo CA a odmietnuť neznámu identitu.

`ssh-keyscan` iba prečíta key, ktorý aktuálne prezentuje endpoint. Neoveruje, že endpoint je legitímny; jeho výstup musí byť porovnaný s dôveryhodným source of truth.

## 5. SSH host certificates

Host certificates umožňujú klientom dôverovať CA namiesto manuálneho zoznamu každého host key. CA podpíše host public key s identities a platnosťou a klient dôveruje riadku `@cert-authority` v `known_hosts`.

Tento model zjednodušuje fleet provisioning a rotation, ale presúva kritickú dôveru na CA private key. CA potrebuje oddelené uloženie, audit, obmedzenú platnosť certifikátov a revocation proces.

Certificates neriešia DNS alebo inventory chybu automaticky. Host certificate musí obsahovať identity, cez ktoré sa klient pripája, inak validácia správne zlyhá.

## 6. User public-key authentication

Pri public-key authentication klient dokáže vlastníctvo private key podpisom session-bound dát. Private key sa na server neposiela.

```text
Client ponúkne public key
  ↓
Server skontroluje policy a authorized key
  ↓
Client podpíše challenge/session data
  ↓
Server overí podpis
```

```bash
ssh-keygen -t ed25519 -a 100
```

- `id_ed25519` — private key; musí zostať tajný a má byť chránený passphrase alebo hardvérovým tokenom.
- `id_ed25519.pub` — public key; možno ho bezpečne distribuovať do `authorized_keys` alebo identity systému.

Public key je authentication credential. Jeho kompromitácia neumožní podpis bez private key, ale stále odhaľuje identity a môže byť zneužitý pri nesprávnom provisioning procese.

## 7. `authorized_keys`

Server typicky načíta povolené public keys z `~/.ssh/authorized_keys` alebo z externého commandu definovaného policy. Prístup závisí nielen od obsahu súboru, ale aj od user identity, ownershipu, permissions, `StrictModes`, SELinux labels a `Match` blocks.

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R "$USER":"$(id -gn)" ~/.ssh
```

Mode `600` nie je magická hodnota sama osebe. Server musí dôverovať celej path od home directory po súbor; writable parent directory pre cudzieho používateľa môže umožniť nahradenie credentialu.

## 8. Key restrictions

Každý `authorized_keys` entry môže obmedziť, čo key smie vykonať:

```text
from="198.51.100.0/24",restrict,command="/usr/local/bin/backup" ssh-ed25519 AAAA...
```

- `from=` — obmedzí akceptovanie keyu podľa source address, ale treba počítať s NAT a proxy pathom.
- `command=` — vynúti jeden server-side command bez ohľadu na požiadavku klienta.
- `no-port-forwarding`, `no-agent-forwarding`, `no-pty` alebo `restrict` — znižujú channel capabilities.

Automation key nemá automaticky potrebovať interactive shell. Forced command a explicitné obmedzenia zmenšujú blast radius kompromitovaného private keyu.

## 9. Password a keyboard-interactive authentication

Password authentication posiela credential cez už šifrovaný transport, ale jeho bezpečnosť závisí od kvality hesla, rate limiting a identity policy. Keyboard-interactive často používa PAM a môže implementovať MFA alebo ďalšie challenge mechanizmy.

```text
Transport je šifrovaný
  ≠
Password je silný
  ≠
Account policy je bezpečná
```

Vypnutie password authentication je vhodné až po overení alternatívneho recovery prístupu. Nesprávna zmena môže zablokovať administráciu, preto treba testovať novú session ešte pred zatvorením existujúcej.

## 10. Authentication methods a `sshd_config`

Server policy môže vyžadovať jednu alebo kombináciu metód. `AuthenticationMethods` napríklad umožní vyžadovať public key a následne MFA-backed keyboard-interactive.

```sshconfig
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

Presná syntax a PAM integration sa líšia podľa distribúcie. Efektívnu konfiguráciu treba overiť cez `sshd -T`, nie iba čítaním jedného súboru.

## 11. Client key selection

Klient môže načítať keys z default paths, configu a agentu. Ak ponúkne priveľa identities, server môže dosiahnuť `MaxAuthTries` skôr než klient skúsi správny key.

```sshconfig
Host app-prod
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/id_ed25519_prod
    IdentitiesOnly yes
```

```bash
ssh -G app-prod
ssh -vvv app-prod
```

`ssh -G` ukáže efektívnu client configuration po aplikovaní `Host` blocks. `IdentitiesOnly yes` obmedzí ponuku na explicitne nakonfigurované identities a znižuje nepredvídateľnosť agentu.

## 12. `ssh-agent`

`ssh-agent` drží odomknuté private keys alebo odkazy na hardware-backed keys a vykonáva podpisové operácie cez Unix socket. Program s prístupom k agent socketu nevie bežne exportovať private key, ale môže požiadať agent o podpis.

```bash
ssh-add ~/.ssh/id_ed25519
ssh-add -l
ssh-add -t 1h ~/.ssh/id_ed25519
```

Agent lifetime, socket permissions a key confirmation sú súčasťou security modelu. Dlhodobo odomknutý agent na zdieľanom desktop-e zvyšuje časové okno zneužitia.

## 13. Agent forwarding

Agent forwarding sprístupní lokálny agent socket remote hostu cez SSH channel. Remote host môže počas session požiadať agent o podpis a použiť ho na lateral movement, hoci private key priamo nevidí.

```bash
ssh -A bastion
```

Kompromitovaný bastion alebo root na remote hoste môže forwarding zneužiť. Preferovaný model je `ProxyJump`, workload identity alebo explicitné krátkodobé credentials; agent forwarding sa má povoliť iba tam, kde je jeho riziko akceptované.

## 14. Bastion a `ProxyJump`

Bastion sprostredkuje transport do internej siete. Pri `ProxyJump` klient vytvorí end-to-end SSH spojenie k cieľu cez stream poskytovaný bastionom; private key cieľového hosta sa na bastion neukladá.

```bash
ssh -J user@bastion internal-host
```

```sshconfig
Host internal-*
    User deploy
    ProxyJump bastion.example.com
```

Bastion je security boundary. Potrebuje minimálny inbound scope, silnú identity policy, audit, patching, session monitoring a obmedzenie lateral movementu.

Bastion nemá byť univerzálny zdieľaný server s osobnými keys a nekontrolovanými tools. Jeho kompromitácia poskytuje výhodný observation a pivot point.

## 15. Connection layer a channels

Po autentifikácii SSH multiplexuje viac logických channels cez jeden encrypted transport. Channel môže byť interactive shell, exec request, SFTP subsystem alebo port forwarding.

To znamená, že „SSH login povolený“ môže implicitne povoľovať aj tunelovanie a agent forwarding. Server policy musí explicitne rozhodnúť, ktoré channel types sú potrebné pre danú rolu.

```sshconfig
AllowTcpForwarding no
X11Forwarding no
PermitTTY no
```

Tieto options možno kombinovať s `Match User`, `Match Group` alebo key-level restrictions. Efektívna policy je výsledkom všetkých vrstiev, nie jedného globálneho nastavenia.

## 16. Remote command a quoting

```bash
ssh host 'systemctl is-active nginx'
status=$?
```

Ak transport a session prebehli, lokálny `ssh` typicky vráti remote command exit status. Status `255` je rezervovaný pre SSH-level failure, napríklad DNS, connect, host-key alebo authentication problém.

Quoting určuje, ktorý shell vykoná expansion:

```bash
ssh host 'printf "%s\n" "$HOME"'
```

Single quotes chránia `$HOME` pred lokálnou expanziou, takže ho vyhodnotí remote shell. Pri nedôveryhodných arguments je bezpečnejšie preniesť dáta cez stdin alebo explicitne serializovať argumenty než skladať command string.

## 17. Interactive session verzus non-interactive command

Interactive login môže načítať iné shell startup files než non-interactive remote command. Preto môže command fungovať po manuálnom prihlásení, ale zlyhať cez `ssh host command` kvôli odlišnému `PATH`, locale alebo environmentu.

Automatizácia nemá závisieť od `.bashrc` side effects. Má používať absolútne paths, explicitné environment values a dokumentovaný remote execution contract.

PTY allocation tiež mení správanie programov, buffering a signal handling. `ssh -T` zakáže pseudo-terminal, zatiaľ čo `ssh -t` ho vynúti; voľba má zodpovedať workloadu.

## 18. Local port forwarding

```bash
ssh -L 127.0.0.1:15432:db.internal:5432 bastion
```

Klient vytvorí lokálny listening socket. Každé spojenie pošle cez SSH transport na bastion a bastion následne otvorí TCP connection k `db.internal:5432` zo svojho network contextu.

```text
Local application
  ↓ localhost:15432
SSH client
  ↓ encrypted channel
Bastion
  ↓ TCP from bastion network
Database
```

DNS meno `db.internal` sa pri bežnom `-L` resolveuje na strane SSH servera/bastionu. Diagnostika preto musí preveriť reachability z bastionu, nie z klienta.

## 19. Remote port forwarding

```bash
ssh -R 127.0.0.1:8080:localhost:3000 remote-host
```

Remote SSH server vytvorí listening socket a traffic tuneluje späť ku klientovi, ktorý sa pripája na svoj `localhost:3000`. Bind address a dostupnosť zvonku ovplyvňuje `GatewayPorts` a server policy.

Remote forwarding môže nečakane publikovať lokálnu službu do vzdialenej siete. Má byť obmedzený cez `AllowTcpForwarding`, `PermitListen` a firewall.

## 20. Dynamic forwarding

```bash
ssh -D 127.0.0.1:1080 bastion
```

Dynamic forwarding vytvorí lokálny SOCKS proxy. Aplikácia posiela destination cez SOCKS protocol a SSH server otvára výsledné remote connections.

DNS môže byť resolveovaný lokálne alebo remote podľa SOCKS mode a client application. Pri privacy alebo split-DNS scenári treba túto vlastnosť explicitne overiť.

SOCKS tunnel môže obísť segmentáciu a monitoring. Nie je to iba convenience feature; je to general-purpose egress capability.

## 21. SFTP a SCP

SFTP je file-transfer subsystem cez SSH channels. Moderné OpenSSH verzie môžu používať SFTP protocol aj pre `scp`, takže správanie sa nemusí zhodovať so starým SCP protocolom.

Bezpečný deployment pattern zahŕňa:

1. **Upload do temporary path** — neúplný súbor ešte nie je viditeľný ako finálny artifact.
2. **Overenie checksumu alebo podpisu** — transport encryption nepreukazuje, že používateľ poslal správnu verziu.
3. **Nastavenie ownera a mode** — artifact dostane explicitné runtime permissions.
4. **Atomic rename** — finálna cesta sa zmení jednou filesystem operáciou v rámci rovnakého filesystemu.
5. **Overenie výsledku** — deployment nesmie považovať úspešný transfer automaticky za funkčnú službu.

## 22. Client configuration precedence

OpenSSH client číta command-line options, user config a system config s pravidlom „prvá získaná hodnota typicky vyhráva“ pre mnohé options. Poradie `Host` blocks preto ovplyvňuje výsledok.

```bash
ssh -G target
```

Efektívna konfigurácia môže obsahovať proxy, identity, hostname canonicalization a host-key policy z viacerých súborov. Pri diagnostike je `ssh -G` autoritatívnejší než čítanie jedného predpokladaného blocku.

Wildcards majú byť navrhnuté opatrne. Široký `Host *` block umiestnený príliš skoro môže nastaviť hodnotu, ktorú neskorší špecifický block už neprepíše.

## 23. Server configuration a precedence

OpenSSH server číta hlavný config a podľa distribúcie aj include súbory. `Match` blocks menia policy pre konkrétne users, groups, addresses alebo ďalšie conditions.

```bash
sshd -t
sshd -T
sshd -T -C user=deploy,host=server,addr=198.51.100.10
```

- `sshd -t` — overí syntax a dostupnosť host keys.
- `sshd -T` — vypíše efektívnu globálnu konfiguráciu.
- `sshd -T -C` — vyhodnotí aj podmienené `Match` rules pre konkrétny connection context.

Pred reloadom treba ponechať recovery session, validovať config a otvoriť novú testovaciu session. Existujúce spojenie môže prežiť chybný reload a vytvoriť falošný pocit, že nový login funguje.

## 24. Hardening ako model hrozieb

SSH hardening má znižovať pravdepodobnosť credential compromise, online guessing, privilege escalation a lateral movement. Neexistuje jeden univerzálny config pre všetky prostredia.

- Zakázanie direct root loginu — oddeľuje osobnú identitu od privilege transition a zlepšuje audit.
- Public-key alebo MFA authentication — znižuje závislosť od opakovateľných hesiel.
- Allowlist users/groups — obmedzí, ktoré účty vôbec môžu vstúpiť cez SSH.
- Network allowlist — znižuje exposure, ale nenahrádza authentication.
- Forwarding restrictions — zabránia použitiu servera ako neplánovaného network pivotu.
- Short-lived certificates — zjednodušujú expiry a revocation oproti permanentným keys.

Zmena portu znižuje scanner noise, ale nemení cryptographic alebo identity boundary. Nemá sa vydávať za hlavný security control.

## 25. Key lifecycle a revocation

Permanentný key bez ownera, expiry a evidence je technický dlh. Každý key má mať identitu vlastníka, účel, scope, provisioning source a revocation path.

Revocation môže zahŕňať odstránenie z `authorized_keys`, zrušenie certificate serialu/principal, aktualizáciu `RevokedKeys` alebo deaktiváciu identity v central systeme. Zmena musí byť distribuovaná na všetky relevantné hosts.

Key rotation bez inventory často ponechá starý key aktívny. Overenie musí testovať, že nový credential funguje a starý je skutočne odmietnutý.

## 26. ControlMaster multiplexing

Client multiplexing umožní viacerým sessions zdieľať jeden transport. Znižuje latency a počet handshakov, ale control socket sa stáva citlivým lokálnym capability endpointom.

```sshconfig
Host *.corp.example
    ControlMaster auto
    ControlPath ~/.ssh/cm-%C
    ControlPersist 5m
```

Permissions na control socket directory musia brániť cudzím používateľom otvoriť nové channels cez existujúce authenticated connection. Multiplexing môže tiež skryť zmeny host-key alebo authentication policy, kým starý transport zostáva otvorený.

## 27. Server-side process a privilege model

`sshd` master process typicky počúva s privilege potrebným na prijatie spojenia a vytvára per-connection processes. Po autentifikácii nastaví user credentials, groups, environment, PAM session a spustí shell alebo command.

Úspešná SSH authentication preto neznamená automaticky úspešný shell. Account môže mať neplatný shell, expired state, PAM restriction, chýbajúci home alebo SELinux denial.

Pri incidente treba odlíšiť pre-auth transport failure, authentication failure a post-auth session setup failure.

## 28. Debugging klienta

```bash
ssh -vvv host
```

Debug output treba čítať ako sekvenciu:

1. **Config loading** — ktoré files a `Host` blocks vytvorili effective settings.
2. **Name resolution a connect** — aká IP/family a port sa použili.
3. **Algorithm negotiation** — či existuje spoločný KEX, host-key a cipher set.
4. **Host verification** — ktorý key server prezentoval a s čím sa porovnal.
5. **Identity offering** — ktoré public keys klient ponúkol a ktoré agent odmietol alebo použil.
6. **Authentication result** — aké metódy server povoľuje a prečo pokus zlyhal.
7. **Channel setup** — či sa otvoril shell, exec, subsystem alebo forwarding channel.

Debug log môže obsahovať usernames, hostnames, paths a policy details. Pred zdieľaním sa musí redigovať.

## 29. Server-side diagnostika

```bash
systemctl status sshd
journalctl -u sshd -b
ss -lntp | grep ':22'
sshd -T
```

Pri `Permission denied (publickey)` treba overiť celý decision path:

1. **Správny user a target host** — klient môže používať iný alias, proxy alebo username.
2. **Ponúkaný key** — `ssh -vvv` ukáže, či klient vôbec poslal očakávanú identity.
3. **Effective server policy** — `sshd -T -C` odhalí `Match` blocks, `AuthorizedKeysFile` a authentication methods.
4. **Account state** — účet môže byť locked, expired alebo mať nepovolený shell.
5. **Path ownership a permissions** — home, `.ssh` a `authorized_keys` musia prejsť `StrictModes` kontrolou.
6. **Key content a restrictions** — public key musí sedieť a `from=` alebo forced-command policy nesmie connection odmietnuť.
7. **PAM a LSM** — PAM account rule alebo SELinux/AppArmor môže zablokovať session aj pri správnom keyu.
8. **Server logs** — presný dôvod je často viditeľný iba na serveri.

## 30. Diagnostika port forwardingu

Forwarding má dve TCP časti: SSH transport a connection z endpointu, ktorý forwarding vykonáva, k cieľu. Obe treba testovať samostatne.

Pri `ssh -L`:

1. Over, že lokálny listening socket existuje cez `ss -lntp`.
2. Over SSH session a server policy `AllowTcpForwarding`/`PermitOpen`.
3. Z bastionu over DNS a TCP reachability cieľa.
4. Použi `ssh -vvv` na zobrazenie channel open failure.
5. Over, či local bind nie je obmedzený iba na inú address family.

„SSH spojenie funguje“ nepreukazuje, že bastion dokáže dosiahnuť forward destination.

## 31. Anti-patterny

### `StrictHostKeyChecking=no` v automatizácii

Pipeline akceptuje ľubovoľný server, ktorý odpovie na route alebo DNS meno. Šifrovanie zostáva, ale identita protistrany nie je overená, takže MITM môže získať príkazy a dáta.

### Private keys uložené na bastione

Každý používateľ kopíruje osobné keys na zdieľaný jump host. Kompromitácia bastionu potom odhalí reusable credentials; `ProxyJump` alebo krátkodobá identity tento risk výrazne znižuje.

### Jeden neobmedzený automation key

Rovnaký permanentný key má interactive shell, forwarding a sudo na celej fleet. Forced commands, principals, source restrictions a oddelené role znižujú blast radius.

### Debug riešený vypnutím bezpečnosti

Pri probléme sa vypne host verification, permissions check alebo authentication policy. Tým sa odstráni dôkaz o príčine a môže vzniknúť trvalá security diera; správny postup zbiera client/server evidence po jednotlivých vrstvách.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi host authentication a user authentication?
2. Prečo prvý fingerprint treba overiť nezávislým kanálom?
3. Prečo `ssh-keyscan` sám nevytvára dôveru?
4. Ako prebieha public-key authentication bez prenosu private keyu?
5. Prečo môže veľa keys v agente spôsobiť `Too many authentication failures`?
6. Aké riziko prináša agent forwarding?
7. Ako sa `ProxyJump` líši od kopírovania keyu na bastion?
8. Kde sa resolveuje destination pri local port forwardingu?
9. Prečo remote command môže mať iný environment než interactive shell?
10. Ako key-level restrictions znižujú blast radius automation credentialu?
11. Ako `sshd -T -C` pomáha pri `Match` blocks?
12. Ako by si odlíšil TCP, host-key, user-authentication a session-setup failure?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Linux networking](linux-networking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Cron a systemd timers →](cron-and-systemd-timers.md)
<!-- KNOWLEDGE-NAVIGATION:END -->