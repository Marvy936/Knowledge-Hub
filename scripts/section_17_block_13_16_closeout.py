from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected closeout block not found in {path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    print(f"expanded {path.relative_to(ROOT)}")


user_storage = SECTION / "user-storage-synchronization-cache-semantics.md"
replace_once(
    user_storage,
    """## 4. User Storage SPI capability model

Custom provider implementuje `UserStorageProvider` a factory, ale reálne operácie prichádzajú cez capability interfaces. Provider nemá predstierať capabilities, ktoré external store nevie authoritative vykonať.

- `UserLookupProvider` poskytuje lookup podľa ID, username alebo emailu a je základ loginu.
- `UserQueryMethodsProvider` a `UserCountMethodsProvider` podporujú searches, pagination a Admin Console inventory.
- `UserRegistrationProvider` umožňuje create/remove users.
- `UserBulkUpdateProvider` podporuje scoped bulk mutation.
- `CredentialInputValidator` validuje credential types.
- `CredentialInputUpdater` zapisuje credentials.

```java
""",
    """## 4. User Storage SPI capability model

Custom provider implementuje `UserStorageProvider` a factory, ale reálne operácie prichádzajú cez capability interfaces. Keycloak zisťuje supported behavior podľa implementovaných interfaces a potom volá odlišné methods pri login-e, user searchi, Admin Console inventory, credential update alebo synchronization. Provider preto nemá deklarovať capability iba preto, že dokáže podobnú operáciu emulovať; každá capability musí mať authoritative source, transaction boundary, pagination alebo conflict semantics a explicitné failure správanie.

`UserLookupProvider` poskytuje lookup podľa internal storage ID, username alebo emailu a je základom authentication resolution. `UserQueryMethodsProvider` a `UserCountMethodsProvider` sú samostatná inventory capability: určujú filtering, pagination a count completeness pre Admin Console a Admin REST, preto successful lookup jedného usera nepreukazuje kompletný query surface. `UserRegistrationProvider` vlastní create/remove lifecycle a musí definovať stable external ID, duplicate detection a delete direction. `UserBulkUpdateProvider` pridáva scoped bulk mutation, pri ktorej sa per-item výsledky nesmú schovať za aggregate success.

Credential capabilities majú odlišnú authority než profile lookup. `CredentialInputValidator` rozhoduje, ktoré credential types provider vie authoritative overiť a čo znamená disabled, expired alebo unavailable source. `CredentialInputUpdater` zapisuje alebo odstraňuje credential a musí riešiť policy, partial external/local commit a descendant sessions. Provider môže validovať LDAP password a súčasne odmietať jeho update; implementácia jedného interface preto nesmie implicitne deklarovať druhý.

```java
""",
)

authz = SECTION / "authorization-services-resources-scopes-policies-permissions.md"
replace_once(
    authz,
    """## 3. PAP, PDP, PEP a PIP

Authorization Services rozdeľujú zodpovednosti:

- **Policy Administration Point (PAP)** spravuje resources, scopes, policies a permissions cez Admin Console, Admin REST alebo Protection API.
- **Policy Decision Point (PDP)** vyhodnocuje permissions a policies pre authorization request.
- **Policy Enforcement Point (PEP)** v resource serveri zastaví alebo povolí request podľa rozhodnutia.
- **Policy Information Point (PIP)** dodáva identity, attributes a runtime context použitý policy evaluationom.

```text
""",
    """## 3. PAP, PDP, PEP a PIP

Authorization Services rozdeľujú administration, rozhodovanie, dodanie contextu a enforcement medzi štyri odlišné responsibility boundaries. Toto rozdelenie je dôležité pri dokazovaní incidentu: správna policy uložená cez PAP ešte nepreukazuje, že PDP načítal intended generation; správny PDP deny nepreukazuje, že PEP zastavil handler; complete identity token nepreukazuje, že PIP dodal current object ownership alebo transaction amount.

**Policy Administration Point (PAP)** spravuje resources, scopes, policies a permissions cez Admin Console, Admin REST alebo Protection API. Jeho výstupom je desired authorization graph s konkrétnymi internal IDs a references. **Policy Decision Point (PDP)** tento graph vyhodnotí pre exact subject, client, resource, scopes a context a vytvorí grant, deny alebo error verdict. PDP nevykonáva business mutation a nepozná automaticky current database object, pokiaľ ho request/PIP neposkytne.

**Policy Information Point (PIP)** dodáva policy inputs ako token claims, user/group/role state, pushed claims, time alebo application context. Každý input potrebuje authority a freshness; client-supplied tenant claim nie je automaticky trusted. **Policy Enforcement Point (PEP)** mapuje reálny HTTP alebo business request na resource/scopes, získa alebo validuje decision a musí zastaviť handler pred side effectom pri deny alebo neprijateľnom error-e. PEP je preto posledný security writer boundary, nie iba logging middleware.

```text
""",
)

replace_once(
    authz,
    """## 10. Decision strategies

Decision strategy určuje, ako kombinovať policy outcomes:

- **UNANIMOUS** vyžaduje positive result všetkých relevantných policies.
- **AFFIRMATIVE** povolí, ak aspoň jedna policy grantne.
- **CONSENSUS** vyžaduje viac positive než negative decisions; tie resultuje deny.

AFFIRMATIVE môže vytvoriť bypass, ak jedna broad role policy prebije tenant alebo freshness deny. Strategy je súčasť permission aj resource-server graphu a treba ju testovať na complete truth table, nie iba intended positive userovi.
""",
    """## 10. Decision strategies

Decision strategy určuje, ako sa jednotlivé policy outcomes skombinujú do permission verdictu. Nie je to kozmetické nastavenie: rovnaké tri policies nad rovnakým userom môžu pri odlišnej strategy vydať opačný výsledok. Test fixture preto musí zachovať outcomes každého policy node-u aj final strategy na permission a resource-server úrovni.

**UNANIMOUS** vyžaduje positive result všetkých relevantných policies. Je vhodná tam, kde role, tenant ownership, authentication freshness a time window tvoria súčasne povinné preconditions; jeden deny alebo nesplnená podmienka zastaví grant. **AFFIRMATIVE** povolí, ak aspoň jedna policy grantne. Je bezpečná iba vtedy, keď policies reprezentujú skutočne alternatívne rovnocenné authority paths; broad role policy by inak prebila tenant alebo freshness deny. **CONSENSUS** vyžaduje viac positive než negative decisions a pri zhode výsledok deny-ne. Počet policies a ich abstain/error semantics preto priamo menia outcome.

Strategy je súčasť permission aj resource-server graphu a treba ju testovať na complete truth table, nie iba intended positive userovi. Pridanie novej policy môže pri CONSENSUS zmeniť majority a pri AFFIRMATIVE vytvoriť nový bypass, aj keď existujúce policies zostali bez zmeny.
""",
)

token_exchange = SECTION / "token-exchange-impersonation-delegated-access.md"
replace_once(
    token_exchange,
    """## 1. Dominantný subject-token-to-target-token lifecycle

```text
""",
    """## 1. Dominantný subject-token-to-target-token lifecycle

Token exchange vytvára nový credential subject, nie iba nový encoding predecessor tokenu. Requester client musí byť autorizovaný spracovať subject token, target client musí vytvoriť vlastný scope/mapper projection a successor token má samostatný audience, lifetime, session a revocation contract. Lifecycle sa preto číta ako transition medzi dvoma token generations a jednou business operation, nie ako jednoduché „forwardovanie usera“.

Najdôležitejšie je zachovať tri identities: user alebo workload subject, requester/acting client a target resource server. Ak successor token ponechá iba `sub` a API ignoruje acting client, confused-deputy alebo overbroad service môže vykonať operáciu, ktorú user context sám nevysvetľuje. Ak retry vytvorí dva successor tokens, credential duplication nesmie vytvoriť dva business side effects; operation idempotency patrí do downstream API.

```text
""",
)
