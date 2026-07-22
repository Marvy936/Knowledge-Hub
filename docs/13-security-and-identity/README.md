# Security and Identity

Táto sekcia vysvetľuje bezpečnostné ciele, risk, identity, access control, directory služby, federation, cryptography, secrets, vulnerability management, supply-chain security a Zero Trust. Témy budujú najprv stabilné bezpečnostné princípy a až potom konkrétne protokoly, platformy a produkty.

Cieľom nie je vytvoriť checklist nástrojov. Každá kapitola má vysvetliť chránené assets, trust boundaries, threat model, authorization a identity lifecycle, failure modes, audit evidence, recovery a trade-offy medzi confidentiality, integrity a availability.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md),
- [Observability](../12-observability/README.md).

## Odporúčané poradie

1. [CIA triáda](cia-triad.md)

Nasledujúci blok rozšíri základ o Authentication, Authorization and Auditing, least privilege, IAM/RBAC a directory identity modely.

## Cieľ zvládnutia

Po dokončení aktuálnej kapitoly má byť možné:

- vysvetliť Confidentiality, Integrity a Availability ako samostatné bezpečnostné ciele,
- analyzovať trade-offy medzi jednotlivými osami CIA,
- identifikovať assets, threats, vulnerabilities, impacts a risks,
- rozlíšiť preventívne, detekčné, corrective, recovery a compensating controls,
- vysvetliť rozdiel medzi existenciou controlu a assurance o jeho účinnosti,
- aplikovať CIA na data at rest, in transit a in use,
- vytvoriť CIA matrix pre application, cloud, Kubernetes, CI/CD, observability a AI systém,
- navrhnúť validation evidence pre confidentiality, integrity a availability,
- použiť CIA pri incident triage, containment a recovery rozhodovaní,
- rozpoznať, že privacy, authenticity, accountability a safety rozširujú základný CIA model.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| CIA triáda | Learning | L2 |
