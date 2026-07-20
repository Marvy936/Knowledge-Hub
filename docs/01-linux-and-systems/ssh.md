# SSH

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Linux networking](linux-networking.md), [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
- Súvisiace témy: public-key cryptography, bastion hosts, port forwarding, automation, secrets management

## 1. Definícia

SSH je protokol a sada nástrojov na bezpečné vzdialené prihlásenie, vykonávanie príkazov, prenos súborov a tunelovanie ďalšej komunikácie cez šifrovaný kanál.

OpenSSH typicky zahŕňa:

- klienta `ssh`,
- server `sshd`,
- `scp` a `sftp`,
- key tools `ssh-keygen`,
- agent `ssh-agent`,
- utility ako `ssh-keyscan` a `ssh-copy-id`.

## 2. Tri vrstvy SSH spojenia

Zjednodušene:

```text
1. Transport layer
   - key exchange
   - server authentication
   - encryption a integrity

2. User authentication
   - public key
   - password
   - keyboard-interactive / PAM

3. Connection layer
   - shell
   - command execution
   - SFTP
   - port forwarding
   - multiple channels v jednom spojení
```

Server sa autentifikuje host key. Používateľ sa následne autentifikuje vlastnou metódou.

## 3. Host keys a `known_hosts`

Server má host private keys, typicky v:

```text
/etc/ssh/ssh_host_*_key
```

Klient si server identity uloží do:

```text
~/.ssh/known_hosts
```

Pri prvom spojení klient zobrazí fingerprint. Jeho bezpečné overenie má prebehnúť cez nezávislý dôveryhodný kanál.

Pri zmene host key klient varuje:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

Možné príčiny:

- legitímna reinštalácia servera,
- zmena IP/DNS targetu,
- load balancer alebo reused address,
- man-in-the-middle útok.

Neodstraňuj záznam automaticky bez overenia novej identity.

## 4. User public-key authentication

Klient drží private key a server authorized public key.

```text
Client private key
  ↓ podpíše challenge/session data
Server
  ↓ overí podpis verejným kľúčom
Authentication success
```

Private key sa neposiela na server.

Generovanie moderného key pair:

```bash
ssh-keygen -t ed25519 -a 100
```

Súbory:

```text
~/.ssh/id_ed25519       private key
~/.ssh/id_ed25519.pub   public key
```

Public key sa na serveri pridáva do:

```text
~/.ssh/authorized_keys
```

## 5. Permissions

OpenSSH môže odmietnuť nebezpečne writable paths.

Typické permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

Dôležité je aj ownership a permissions parent home directory. Presné kontroly ovplyvňuje `StrictModes` a server configuration.

## 6. SSH agent

`ssh-agent` drží odomknuté private keys v pamäti procesu, aby používateľ nemusel opakovane zadávať passphrase.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```

Agent neposkytuje private key priamo aplikácii; vykoná podpisovú operáciu.

Agent forwarding:

```bash
ssh -A bastion
```

umožní remote hostu používať lokálny agent socket. Kompromitovaný remote host môže počas session zneužiť agent na podpis. Preferuj `ProxyJump` a explicitnú konektivitu pred agent forwardingom.

## 7. Client configuration

`~/.ssh/config`:

```sshconfig
Host app-prod
    HostName 203.0.113.10
    User deploy
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Použitie:

```bash
ssh app-prod
```

Konfigurácia znižuje copy-paste chyby a umožňuje explicitne definovať identity, bastion a host key policy.

Efektívna konfigurácia:

```bash
ssh -G app-prod
```

## 8. Bastion a ProxyJump

```bash
ssh -J user@bastion internal-host
```

Config:

```sshconfig
Host internal-*
    User deploy
    ProxyJump bastion.example.com
```

ProxyJump vytvorí transport cez bastion bez potreby ukladať private key na bastione.

Bastion je security boundary a potrebuje:

- minimálny access,
- audit,
- patching,
- MFA alebo central identity podľa prostredia,
- session controls,
- obmedzenie lateral movement.

## 9. Remote commands a exit status

```bash
ssh host 'systemctl is-active nginx'
echo $?
```

Lokálny `ssh` typicky vráti remote command exit status, ak session prebehla. Špeciálny status `255` často znamená SSH-level failure, napríklad DNS, connection alebo authentication problém.

Quoting je kritické:

```bash
ssh host 'echo "$HOME"'
```

Single quotes zabezpečia, že `$HOME` expanduje remote shell, nie lokálny shell.

## 10. Port forwarding

### Local forwarding

```bash
ssh -L 15432:db.internal:5432 bastion
```

```text
local localhost:15432
  ↓ SSH tunnel
bastion
  ↓ TCP
 db.internal:5432
```

### Remote forwarding

```bash
ssh -R 8080:localhost:3000 remote-host
```

Remote host počúva na definovanom endpoint-e a traffic tuneluje späť ku klientovi.

### Dynamic forwarding

```bash
ssh -D 1080 bastion
```

Vytvorí lokálny SOCKS proxy.

Forwarding môže obísť network segmentation, preto sa server-side riadi napríklad `AllowTcpForwarding`, `PermitOpen` a bind policies.

## 11. SFTP a SCP

```bash
sftp user@host
scp file user@host:/tmp/
```

Moderné OpenSSH môže implementovať `scp` cez SFTP protocol. Pri automatizácii preferuj kontrolovateľný transfer s explicitnými permissions, checksum validation a atomic placement.

Príklad bezpečnejšieho deployment patternu:

```text
upload do temporary path
  ↓
verify checksum/signature
  ↓
set owner a mode
  ↓
atomic rename na final path
```

## 12. Server configuration

Hlavný config:

```text
/etc/ssh/sshd_config
/etc/ssh/sshd_config.d/*.conf
```

Validácia:

```bash
sudo sshd -t
sudo sshd -T
```

- `-t` kontroluje syntax a keys,
- `-T` zobrazí efektívnu konfiguráciu.

Po zmene:

```bash
sudo systemctl reload sshd
```

Názov unit môže byť `ssh` alebo `sshd` podľa distribúcie.

Pred reloadom nechaj otvorenú existujúcu session a otestuj novú paralelnú session. Chybná konfigurácia môže odpojiť administratívny prístup.

## 13. Hardening

Typické princípy:

```sshconfig
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers deploy admin
MaxAuthTries 3
```

Presná politika závisí od recovery modelu a identity architecture.

Dôležitejšie než samotná zmena portu:

- strong authentication,
- aktuálny server,
- least privilege,
- firewall allowlist tam, kde je možná,
- MFA/central identity,
- monitoring brute-force a neštandardných loginov,
- oddelenie user a privileged access,
- bezpečný host key lifecycle.

Zmena portu znižuje noise automatizovaných scannerov, ale nie je zásadný authentication control.

## 14. Debugging klienta

```bash
ssh -v host
ssh -vv host
ssh -vvv host
```

Debug output ukáže:

- config files,
- resolved host,
- connection attempt,
- negotiated algorithms,
- host key verification,
- ponúkané identities,
- authentication methods,
- channel setup.

Pozor na zdieľanie debug logu: môže obsahovať usernames, hostnames, paths a infraštruktúrne detaily.

## 15. Server-side diagnostika

```bash
systemctl status sshd
journalctl -u sshd -b
ss -lntp | grep ':22'
sshd -T
```

Pri authentication failure kontroluj:

- user existuje a má valid shell,
- account nie je locked/expired,
- home a `.ssh` ownership,
- `authorized_keys` path a syntax,
- `AllowUsers`/`DenyUsers`/Match blocks,
- PAM policy,
- SELinux labels,
- key algorithm policy.

## 16. `authorized_keys` restrictions

Public key entry môže mať options:

```text
from="198.51.100.0/24",no-agent-forwarding,no-port-forwarding,command="/usr/local/bin/backup" ssh-ed25519 AAAA...
```

To umožňuje obmedziť key na:

- source addresses,
- forced command,
- zákaz PTY,
- zákaz agent/port/X11 forwarding.

Je to vhodné pre automation keys, kde plný interactive shell nie je potrebný.

## 17. Automation a host key verification

Nebezpečný pattern:

```bash
ssh -o StrictHostKeyChecking=no host command
```

Môže akceptovať neoverený server a oslabiť ochranu proti MITM.

Lepší model:

- spravovať `known_hosts` ako dôveryhodnú konfiguráciu,
- distribuovať host CA a používať SSH certificates,
- používať trusted inventory,
- rotovať keys kontrolovaným procesom.

`ssh-keyscan` iba načíta prezentovaný public host key. Sám nedokazuje, že patrí správnemu serveru.

## 18. Troubleshooting scenár

`Permission denied (publickey)`:

1. spusti `ssh -vvv host`,
2. over, ktorú identity klient ponúka,
3. použi `IdentitiesOnly yes`, ak agent ponúka veľa keys,
4. over server logs,
5. skontroluj user, home, ownership a modes,
6. porovnaj public key s `authorized_keys`,
7. over Match blocks a effective `sshd -T`,
8. skontroluj SELinux/PAM/account state,
9. otestuj bez vypnutia host key verification.

## 19. Časté omyly

### „Public key sa kopíruje ako private key na server“

Nie. Server potrebuje iba public key.

### „Agent forwarding je bezpečný, lebo private key neopustí laptop“

Private key neopustí agent, ale kompromitovaný remote host môže počas session žiadať podpisové operácie.

### „Zmena SSH portu vyrieši bezpečnosť“

Zníži noise, nie riziko slabých credentials alebo zraniteľného servera.

### „`ssh-keyscan` overí identitu servera“

Iba získa key prezentovaný endpointom; identitu treba overiť dôveryhodným kanálom.

### „Reload sshd je bez rizika“

Chybná policy môže zablokovať nové sessions. Najprv validuj a ponechaj recovery session.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi host authentication a user authentication?
2. Prečo private key nemusí opustiť klienta?
3. Čo presne chráni `known_hosts`?
4. Aké riziko prináša agent forwarding?
5. Aký je rozdiel medzi local, remote a dynamic forwardingom?
6. Prečo `ssh-keyscan` nie je dôkaz identity?
7. Ako zistíš efektívnu client a server konfiguráciu?
8. Ako navrhneš obmedzený automation key bez interactive shellu?
