# ConfigMap a Secret

ConfigMap a Secret sú API objekty pre runtime configuration, ale medzi hodnotou uloženou v API a hodnotou, ktorú aplikácia skutočne používa, existuje viac krokov. Pod template musí source referencovať, kubelet ho musí materializovať ako environment alebo volume, container musí vzniknúť a process musí hodnotu načítať. Zmena source objektu preto sama osebe neznamená, že všetky bežiace repliky používajú novú configuration generation.

Pri `payments-api` drží ConfigMap necauthentication nastavenia a Secret databázovú credential generation. Aplikácia publikuje cez `/version` iba bezpečné identifikátory `config_generation` a `secret_epoch`, nie samotné tajomstvo. Vďaka tomu možno rollout overiť bez úniku secretu.

## ConfigMap pre ne-secret konfiguráciu

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payments-api-config-c52
  namespace: production
data:
  application.yaml: |
    listenAddress: ":8080"
    logLevel: "info"
    paymentTimeout: "3s"
  CONFIG_GENERATION: "C52"
```

ConfigMap nie je schema-validovaná aplikačná konfigurácia. API server overí Kubernetes tvar a limity objektu, nie význam `paymentTimeout`. Aplikácia alebo samostatný validator musí kontrolovať syntax, povolené hodnoty a cross-field invariants.

Versionované meno `payments-api-config-c52` vytvára jasnú generáciu. Alternatívou je stabilné meno plus checksum annotation v Pod template-u. V oboch prípadoch musí zmena, ktorá vyžaduje process restart, vytvoriť novú Pod template revision.

## Secret nie je automaticky bezpečný iba názvom

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: payments-db-se08
  namespace: production
type: Opaque
stringData:
  username: payments_api
  password: "<injected-by-secret-management>"
  SECRET_EPOCH: "SE08"
```

Base64 v poli `data` je encoding, nie encryption. Bez encryption at rest a správnej key management konfigurácie môžu byť values v etcd čitateľné pre kompromitovanú control-plane identity. RBAC, audit, admission, external secret flow a node/runtime boundary ostávajú rozhodujúce.

Secret sa nemá ukladať do Git repozitára ako plaintext. Manifest môže obsahovať iba reference, encrypted source alebo external secret contract podľa zvolenej platformy.

## Environment variables sú snapshot pri štarte

Pod môže načítať jednu hodnotu:

```yaml
env:
  - name: CONFIG_GENERATION
    valueFrom:
      configMapKeyRef:
        name: payments-api-config-c52
        key: CONFIG_GENERATION
```

Alebo všetky keys:

```yaml
envFrom:
  - configMapRef:
      name: payments-api-config-c52
  - secretRef:
      name: payments-db-se08
```

Environment sa zostaví pri container create. Neskoršia zmena ConfigMap alebo Secretu nemení environment bežiaceho procesu. Potrebný je container/Pod replacement.

`envFrom` je pohodlné, ale môže neplánovane rozšíriť aplikačný input a skryť kolízie názvov. Pri citlivých alebo kritických hodnotách je explicitný `env` contract čitateľnejší.

## Volume projection má iné update semantics

```yaml
volumes:
  - name: config
    configMap:
      name: payments-api-config-c52
  - name: db-secret
    secret:
      secretName: payments-db-se08
      defaultMode: 0400
```

```yaml
volumeMounts:
  - name: config
    mountPath: /etc/payments/config
    readOnly: true
  - name: db-secret
    mountPath: /var/run/secrets/payments-db
    readOnly: true
```

Kubelet môže projected files aktualizovať podľa svojho sync a cache modelu. Aktualizácia však nie je okamžitá transakcia naprieč všetkými Nodes a files. Aplikácia musí súbor znovu načítať alebo byť reštartovaná. Process, ktorý otvoril TLS key alebo databázové connection pri štarte, môže ďalej používať starú hodnotu aj po zmene súboru.

Mounted source, bytes na Node-e a process-loaded state sú tri samostatné observation points.

## `subPath` mení očakávania

Mount jedného súboru cez `subPath` sa typicky neaktualizuje rovnakým spôsobom ako celý projected volume.

```yaml
volumeMounts:
  - name: config
    mountPath: /etc/payments/application.yaml
    subPath: application.yaml
```

Ak tím očakáva hot reload, `subPath` môže vytvoriť prekvapenie. Contract treba overiť v cieľovej verzii a runtime správaní, nie predpokladať podľa source objektu.

## Immutable objekty

ConfigMap a Secret možno označiť ako immutable:

```yaml
immutable: true
```

Potom sa data nemenia in-place. Nová konfigurácia dostane nový objekt a Pod template sa zmení na novú reference. To zjednodušuje audit a znižuje watch zaťaženie, ale vyžaduje retention a cleanup starých generácií.

Immutable Kubernetes Secret stále potrebuje credential rotation. Immutable znamená iba, že konkrétny API objekt sa nemení; target credential, consumers a revocation majú vlastný lifecycle.

## Deployment rollout cez explicitnú generáciu

```yaml
spec:
  template:
    metadata:
      annotations:
        atlas.example/config-generation: "C52"
        atlas.example/secret-epoch: "SE08"
    spec:
      volumes:
        - name: config
          configMap:
            name: payments-api-config-c52
        - name: db-secret
          secret:
            secretName: payments-db-se08
```

Zmena annotation alebo reference zmení Pod template a vytvorí nový ReplicaSet. Po rollout-e sa nespoliehaj iba na manifest:

```bash
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,CONFIG:.metadata.annotations.atlas\.example/config-generation,SECRET:.metadata.annotations.atlas\.example/secret-epoch,READY:.status.containerStatuses[0].ready'
```

Potom over process-loaded hodnoty cez bezpečný endpoint a reálnu databázovú autentizáciu.

## Secret rotation ako distribuovaný prechod

Bezpečná rotation je viac než update Secretu:

```text
vytvor novú target credential generation
→ vytvor nový Kubernetes Secret
→ zmeň Pod template
→ rolloutni consumers
→ over process-loaded epoch a business calls
→ až potom zruš starú credential generation
→ odstráň staré Kubernetes artifacts podľa retention
```

Ak sa stará credential zruší pred rolloutom všetkých consumers, vzniknú intermittent failures. Ak sa nikdy nezruší, rotation nedokončí security outcome.

## Service account token projection

Automaticky projectované service-account tokeny sú tiež secrets v širokom zmysle, ale majú osobitný lifecycle. Bound token má audience, expiry a väzbu na Pod alebo inú identitu. Aplikácia ho má čítať z projected pathu a klientská knižnica musí zvládnuť rotation.

Statický dlhodobý token uložený v environment variable obchádza tieto vlastnosti a zvyšuje blast radius.

## RBAC a read boundary

Právo `get secrets` v namespace umožňuje čítať secret values. Právo vytvárať Pod môže byť v niektorých modeloch nepriamou cestou k secretu: útočník vytvorí Pod, ktorý Secret mountne.

Preto least privilege posudzuje nielen priamy verb nad Secretom, ale aj workload creation, exec, debug a node access.

```bash
kubectl auth can-i get secrets -n production --as=<identity>
kubectl auth can-i create pods -n production --as=<identity>
```

## Incident: ConfigMap sa zmenila, Pods ostali na starej hodnote

Operátor upravil stabilnú ConfigMap `payments-api-config`. Dashboard ukázal novú value v API, no aplikácie stále používali starý timeout, pretože hodnota bola načítaná cez environment pri štarte.

Kubelet ani Deployment nezlyhali. Neexistovala zmena Pod template-u, takže nevznikol rollout. Oprava zaviedla versionované ConfigMaps a explicitnú generation annotation. Recovery sa overila cez všetky Pod UIDs a `/version`.

## Incident: Secret rotation vytvorila split generation

Polovica Podov bola manuálne zmazaná a dostala nový Secret `SE08`. Druhá polovica pokračovala s `SE07`. Po revokácii starej databázovej credential zlyhávala približne polovica requestov.

Containment dočasne obnovil overlap credential podľa security rozhodnutia. Autoritatívna oprava rolloutla celý Deployment a overila loaded epoch na každej replike. Následne sa SE07 zrušila a audit potvrdil, že sa už nepoužíva.

## Incident: Secret unikol cez debug output

Troubleshooting script vypísal `kubectl get pod -o yaml` a environment do CI logu. Secret value síce nebola priamo v Pod YAML, ale application pri štarte logovala celý config vrátane passwordu.

Oprava zahŕňala okamžitú rotation target credentialu, redakciu logs a zmenu aplikácie. `no_log` alebo Kubernetes Secret typ nechránia plaintext po tom, čo ho consumer vypíše.

## Model, ktorý si treba odniesť

ConfigMap a Secret sú source objekty. Efektívny výsledok vzniká až cez Pod reference, kubelet materialization, container create a process load. Environment je snapshot; mounted files majú asynchrónne update semantics; aplikácia potrebuje reload contract. Secret bezpečnosť zahŕňa etcd, RBAC, workload creation, node access, consumer logs, target credential rotation a revocation.

## Referencie

- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Distribute Credentials Securely Using Secrets](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)
- [Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Job a CronJob](job-cronjob.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ServiceAccount →](serviceaccount.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
