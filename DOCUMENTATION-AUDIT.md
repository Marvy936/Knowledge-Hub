# Documentation learning-depth audit

> Stavový ledger pre kvalitatívny audit učebnej dokumentácie. Automatický heuristický baseline z `scripts/audit_learning_depth.py` zatiaľ nebol na self-hosted runneri úspešne publikovaný. Tento dokument preto transparentne rozlišuje manuálne dokončené review od čakajúceho automatického corpus reportu.

## Audit objective

Cieľom je odhaliť a opraviť kapitoly alebo podkapitoly, ktoré fungujú iba ako rozšírená osnova:

- jedna veta nasledovaná dlhým zoznamom;
- nové odborné pojmy prvýkrát uvedené bez vysvetlenia;
- pomenovanie komponentov bez popisu ich mechanizmu a väzieb;
- zoznam best practices bez threat modelu, podmienok a trade-offov;
- troubleshooting kroky bez vysvetlenia, ktorú hypotézu overujú;
- chýbajúci konkrétny príklad, failure mode alebo recovery boundary.

Požadovaný štandard je definovaný v [`AUTHORING-GUIDE.md`](AUTHORING-GUIDE.md). Odrážky majú sumarizovať už vysvetlený model, nie nahrádzať učebný výklad.

## Corpus scope

- Autoritatívne učebné sekcie: **14**
- Autoritatívne učebné články podľa sekčných `README.md`: **257**
- Praktické laby, troubleshooting scenáre a templates sa kontrolujú samostatne podľa ich účelu.

Automatický audit má po úspešnom behu prejsť všetky `docs/**/*.md` súbory a prepísať tento ledger prioritizovaným reportom. Kým sa tak nestane, žiadna nepreverená kapitola sa nepovažuje za automaticky validovanú.

## Trvalé guardrails dokončené

- [x] `AUTHORING-GUIDE.md` definuje povinný model `čo → prečo → ako → príklad → failure/trade-off`.
- [x] Root `README.md` zakazuje konceptuálne sekcie tvorené iba jednou vetou a zoznamom.
- [x] `templates/topic-template.md` vyžaduje vysvetlenie nových termínov, mechanizmov, dependencies a failure semantics.
- [x] `scripts/audit_learning_depth.py` deteguje list-heavy, thin a term-before-explanation patterns.
- [x] Audit je integrovaný do `.github/workflows/knowledge-navigation.yml`.
- [x] Workflow používa `runs-on: [self-hosted, Linux, X64]` a Python 3.12.
- [ ] Automatický corpus report bol publikovaný self-hosted runnerom.

## Manuálne auditované vzorky mimo Security and Identity

Tieto kapitoly boli otvorené a posúdené ako referenčné vzorky. Majú prevažne súvislý mechanistický výklad; prípadné lokálne medzery budú ďalej zoradené automatickým reportom.

- `docs/00-foundations/sdlc.md`
- `docs/00-foundations/calms.md`
- `docs/09-kubernetes/serviceaccount.md`

Toto nie je úplné schválenie celej príslušnej sekcie.

## Dokončené hĺbkové rewrites

Nasledujúce kapitoly boli manuálne prečítané a prepracované z množstva krátkych hesiel do väčších učebných celkov. Pri každom dôležitom pojme bol doplnený význam, mechanizmus, praktický dôsledok a failure alebo recovery boundary.

| Kapitola | Výsledok auditu a nápravy |
|---|---|
| `zero-trust.md` | Resource-level decision model, dynamic signals, workload attestation, SPIFFE/SPIRE, PE/PA/PEP, delegation, degraded modes a end-to-end access example. |
| `policy-as-code.md` | PAP/PDP/PEP/PIP, input/data schema, revision lifecycle, OPA/Rego, Kubernetes admission, Gatekeeper/Kyverno, exceptions a incident recovery. |
| `image-signing.md` | OCI subject identity, multi-arch signing, Sigstore/Fulcio/Rekor, trust roots, signer authorization, attestations, admission verification a quarantine. |
| `sbom.md` | Subject identity, SPDX/CycloneDX, purl/CPE, relationships, completeness/accuracy/freshness, VEX, OCI distribution, deployment mapping a incident response. |
| `supply-chain-security.md` | Source, dependency, runner, builder, provenance, SLSA, in-toto, TUF, promotion, runtime inventory a recovery trust chain. |
| `threat-modeling.md` | Objectives, DFD, actors, boundaries, STRIDE/CAPEC/ATT&CK/LINDDUN, threat statements, requirements, negative tests a residual risk. |
| `vulnerability-and-patch-management.md` | Inventory, matching, CVSS/EPSS/KEV, exposure/reachability, rings, runtime activation, verification, exceptions a recurrence. |
| `encryption-at-rest-and-in-transit.md` | Threat boundaries, AEAD, envelope encryption, KMS/HSM, key lifecycle, TLS 1.3, Kubernetes encryption a crypto agility. |
| `secrets-management.md` | Secret capability/lifecycle, workload identity, delivery/cache, rotation/revocation, Kubernetes/ESO/CSI, Vault internals, outage a DR. |

## Aktuálna manuálna priorita

1. Federation blok:
   - `saml.md`
   - `openid-connect.md`
   - `oauth-2.md`
2. Identity protocols a directories:
   - `kerberos.md`
   - `ldap.md`
   - `active-directory.md`
3. Authorization foundations:
   - `iam-rbac.md`
   - `least-privilege.md`
   - `authentication-authorization-auditing.md`
   - `cia-triad.md`
4. Následne všetky ostatné sekcie zoradené automatickým score a manuálnou technical review.

## Definition of done pre jednu kapitolu

Kapitola je po hĺbkovom review dokončená iba vtedy, keď:

1. jej opening vysvetľuje, aký problém rieši a kde sa nachádza v širšom systéme;
2. nový termín nie je ponechaný iba ako názov odrážky;
3. actors, state, data alebo decision flow sú vysvetlené v súvislom texte;
4. každý dlhší zoznam má unifying model a praktický dôsledok;
5. major concept cluster má aspoň jeden konkrétny príklad;
6. dependencies, failure semantics a recovery sú explicitné;
7. troubleshooting kroky vysvetľujú, ktorú vrstvu alebo hypotézu overujú;
8. glossary impact a primárne zdroje sú aktuálne;
9. generated navigation ostáva konzistentná;
10. text prešiel manuálnou technical a pedagogical kontrolou, nie iba word-count heuristikou.

## Otvorený blocker automatického baseline-u

`Knowledge documentation` workflow je nakonfigurovaný na self-hosted Linux X64 runner a audit script je súčasťou synchronizačného kroku. Report zatiaľ nebol publikovaný. Možné operational príčiny zahŕňajú offline/busy runner, queue alebo zrušené runs pri rýchlych sekvenčných commitoch v rovnakej concurrency group.

Kým nie je dostupný vygenerovaný report alebo workflow log, príčina sa nepovažuje za potvrdenú. Manuálne review pokračuje nezávisle od tohto blockeru.
