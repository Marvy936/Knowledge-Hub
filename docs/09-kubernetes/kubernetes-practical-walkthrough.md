# Praktický Kubernetes projekt od manifestov po overený rollout

Predchádzajúce kapitoly rozobrali Kubernetes po jednotlivých mechanizmoch. Teraz ich spojíme do jedného malého projektu. Vytvoríme Namespace, ServiceAccount, ConfigMap, Secret contract, Deployment, Service, PodDisruptionBudget, NetworkPolicy a HPA. Manifesty najprv vyrenderujeme a pošleme cez server-side dry-run, potom ich aplikujeme, prečítame skutočný object graph a overíme request cez Service.

Príklad používa rovnakú službu `payments-api` ako Docker sekcia. Image musí byť vopred publikovaný v registry pod immutable digestom. Text používa placeholdery ako `<payments-api-digest>` a `<curl-image-digest>`; pred spustením ich treba nahradiť skutočnými schválenými digestmi.

Cieľom nie je iba dostať šesť Podov do stavu `Running`. Budeme oddeľovať:

```text
source YAML
→ Kustomize rendered model
→ API admitted objects
→ controller graph
→ scheduled a running Pods
→ readiness a EndpointSlice
→ Service request
→ configuration-driven replacement
→ failure diagnosis a recovery
```

## 1. Adresárová štruktúra

Vytvor projekt:

```bash
mkdir -p atlas-payments-kubernetes/overlays/broken-selector
mkdir -p atlas-payments-kubernetes/overlays/broken-readiness
mkdir -p atlas-payments-kubernetes/scripts
cd atlas-payments-kubernetes
```

Výsledná štruktúra bude:

```text
atlas-payments-kubernetes/
├── namespace.yaml
├── serviceaccount.yaml
├── configmap.yaml
├── secret.example.yaml
├── deployment.yaml
├── service.yaml
├── pdb.yaml
├── networkpolicy.yaml
├── hpa.yaml
├── kustomization.yaml
├── overlays/
│   ├── broken-selector/
│   │   └── kustomization.yaml
│   └── broken-readiness/
│       └── kustomization.yaml
└── scripts/
    └── verify.sh
```

Tento adresár je iba source. Kubernetes objects vzniknú až po prijatí manifestov API serverom. Bežiace processes vzniknú ešte neskôr cez controllers, scheduler, kubelet, runtime a CNI.

## 2. Namespace a Pod Security boundary

Vytvor `namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

Namespace vytvára naming a policy scope. Label `enforce=restricted` požiada Pod Security Admission, aby odmietla Pods, ktoré nespĺňajú Restricted policy pre clusterom používanú policy verziu.

V production platforme je vhodné policy version pinovať na verziu overenú pre cieľový cluster a upgradeovať ju vedome. V tomto walkthroughu nechávame server použiť jeho aktuálny contract, aby príklad nepredstieral konkrétnu Kubernetes minor verziu.

Namespace nie je úplná tenant izolácia. RBAC, NetworkPolicy, storage, cloud identity a Node placement zostávajú samostatné boundaries.

Najprv možno vytvoriť iba Namespace:

```bash
kubectl apply -f namespace.yaml
```

Tento krok potrebujeme pred vytvorením Secretu mimo Kustomize balíka.

## 3. ServiceAccount bez implicitného API tokenu

Vytvor `serviceaccount.yaml`:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments-api
  namespace: production
automountServiceAccountToken: false
```

Aplikácia nepotrebuje volať Kubernetes API. Token preto automaticky nemountujeme. Tým znižujeme credential exposure pri compromise aplikácie.

ServiceAccount bez bindingu nemá aplikačné API permissions. Stále môže byť podľa platformy previazaný na external cloud identity, preto sa cloud IAM audit vykonáva osobitne.

## 4. ConfigMap generation `C52`

Vytvor `configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payments-api-config
  namespace: production
data:
  CONFIG_GENERATION: "C52"
  application.yaml: |
    listenAddress: ":8080"
    logLevel: "info"
    paymentTimeout: "3s"
```

ConfigMap obsahuje ne-secret configuration. Kubernetes nevaliduje aplikačný význam `paymentTimeout`; aplikácia alebo samostatný validator musí kontrolovať schema a hodnoty.

Používame stabilné meno a explicitnú generation annotation v Deployment template. Pri zmene konfigurácie upravíme obe hodnoty. Samotná zmena ConfigMap by environment bežiacich procesov nezmenila a Deployment rollout by automaticky nevznikol.

## 5. Secret contract bez uloženia tajomstva do repozitára

Vytvor `secret.example.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: payments-runtime-se08
  namespace: production
type: Opaque
stringData:
  SECRET_EPOCH: "SE08"
  PAYMENTS_SIGNING_KEY: "replace-through-secret-management"
```

Tento súbor je iba dokumentačný vzor a **nie je** uvedený v `kustomization.yaml`. Reálnu hodnotu nevkladaj do Git repozitára.

Pre lokálny lab môžeš Secret vytvoriť zo súboru, ktorý má obmedzené permissions:

```bash
umask 077
printf '%s' "$PAYMENTS_SIGNING_KEY" > /tmp/payments-signing-key

kubectl create secret generic payments-runtime-se08 \
  --namespace production \
  --from-literal=SECRET_EPOCH=SE08 \
  --from-file=PAYMENTS_SIGNING_KEY=/tmp/payments-signing-key \
  --dry-run=client \
  -o yaml \
  | kubectl apply -f -

rm -f /tmp/payments-signing-key
```

V produkcii má Secret vytvoriť schválený secret-management controller alebo deployment flow. Shell environment a history sú tiež credential boundaries.

Secret existence ešte nepreukazuje, že Pod ho mountol alebo že process hodnotu načítal. Overíme aspoň epoch metadata a runtime reference bez vypísania samotného keyu.

## 6. Deployment: jedna úplná Pod template

Vytvor `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: production
  labels:
    app.kubernetes.io/name: payments-api
    app.kubernetes.io/part-of: atlas-payments
spec:
  replicas: 6
  revisionHistoryLimit: 5
  progressDeadlineSeconds: 600
  minReadySeconds: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
        app.kubernetes.io/part-of: atlas-payments
      annotations:
        atlas.example/config-generation: "C52"
        atlas.example/secret-epoch: "SE08"
    spec:
      serviceAccountName: payments-api
      automountServiceAccountToken: false
      terminationGracePeriodSeconds: 45
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        runAsGroup: 65532
        fsGroup: 65532
        seccompProfile:
          type: RuntimeDefault
      nodeSelector:
        kubernetes.io/os: linux
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: payments-api
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                topologyKey: kubernetes.io/hostname
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: payments-api
      containers:
        - name: api
          image: registry.example.com/atlas/payments-api@sha256:<payments-api-digest>
          imagePullPolicy: IfNotPresent
          args:
            - serve
          env:
            - name: LISTEN_ADDRESS
              value: ":8080"
            - name: DATA_PATH
              value: /var/lib/atlas-payments/payments.jsonl
            - name: HEALTHCHECK_URL
              value: http://127.0.0.1:8080/readyz
            - name: CONFIG_GENERATION
              valueFrom:
                configMapKeyRef:
                  name: payments-api-config
                  key: CONFIG_GENERATION
            - name: SECRET_EPOCH
              valueFrom:
                secretKeyRef:
                  name: payments-runtime-se08
                  key: SECRET_EPOCH
            - name: PAYMENTS_SIGNING_KEY_FILE
              value: /var/run/secrets/atlas/PAYMENTS_SIGNING_KEY
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          startupProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 2
            timeoutSeconds: 1
            failureThreshold: 30
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 3
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: config
              mountPath: /etc/payments
              readOnly: true
            - name: runtime-secret
              mountPath: /var/run/secrets/atlas
              readOnly: true
            - name: data
              mountPath: /var/lib/atlas-payments
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: config
          configMap:
            name: payments-api-config
        - name: runtime-secret
          secret:
            secretName: payments-runtime-se08
            defaultMode: 0400
        - name: data
          emptyDir:
            sizeLimit: 64Mi
        - name: tmp
          emptyDir:
            medium: Memory
            sizeLimit: 32Mi
```

### Prečo používame digest

Tag je mutable pointer. Digest identifikuje konkrétny registry artifact. Po štarte ešte prečítame `status.containerStatuses[].imageID`, pretože source image reference nie je konečný runtime dôkaz.

### Prečo je root filesystem read-only

Application image sa počas runtime nemení. Zapisovateľné paths sú explicitné: `/tmp` a `/var/lib/atlas-payments`. `emptyDir` je iba runtime scratch pri tomto stateless walkthroughu. Dáta neprežijú Pod replacement; business persistence by v reálnej aplikácii vlastnila databáza alebo persistentný storage systém.

### Prečo sú probes rozdielne

Startup probe dá aplikácii čas inicializovať sa. Liveness používa plytký `/healthz`. Readiness používa `/readyz` a riadi EndpointSlice eligibility. Ani jedna probe nejde cez Service alebo Gateway, preto rollout neskôr doplníme Service requestom.

### Prečo je anti-affinity iba preferred

Walkthrough má fungovať aj v menšom lab clustri. Preferred anti-affinity a `ScheduleAnyway` topology spread sa snažia repliky rozložiť, ale nezablokujú projekt pri jednej zone alebo malom počte Nodes. Production HA požiadavky môžu používať hard constraints, ale potrebujú zodpovedajúcu kapacitu a surge headroom.

## 7. Service

Vytvor `service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: production
  labels:
    app.kubernetes.io/name: payments-api
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: payments-api
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
```

Service poskytuje stabilné meno `payments-api.production.svc`. Selector vyberá Pods podľa labelu. EndpointSlice controller potom publikuje konkrétne ready Pod endpoints a named port `http` vyrieši na 8080.

Service object sám nepreukazuje existenciu endpointov ani application listenera.

## 8. PodDisruptionBudget

Vytvor `pdb.yaml`:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payments-api
  namespace: production
spec:
  minAvailable: 5
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
```

PDB chráni pred vybranými voluntary disruptions cez eviction API. Nezabráni Node crashu, liveness restartu, Deployment rolling update-u vo všetkých rovnakých semantics ani aplikačnému failure-u.

Pri šiestich replikách povoľuje jednu dobrovoľnú nedostupnú repliku. Cluster potrebuje aspoň päť Ready Podov, aby bežný drain mohol pokračovať.

## 9. NetworkPolicy

Vytvor `networkpolicy.yaml` s viacerými dokumentmi:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-ingress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: edge-system
      ports:
        - protocol: TCP
          port: 8080
    - from:
        - podSelector:
            matchLabels:
              access: payments-client
      ports:
        - protocol: TCP
          port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payments-api-dns-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: verifier-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      access: payments-client
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: payments-api
      ports:
        - protocol: TCP
          port: 8080
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

Prvý dokument izoluje všetky Pods v namespace pre ingress aj egress. Ďalšie policies pridávajú povolené flows. Kubernetes NetworkPolicy je aditívna allow policy, nie ordered firewall list.

DNS rule predpokladá resolver path do `kube-system`. Cluster s NodeLocal DNSCache alebo iným modelom potrebuje policy prispôsobiť actual destination. Walkthrough má overiť policy v cieľovom clustri, nie predstierať univerzálny DNS layout.

Ingress z Node-local kubelet probes má implementation-specific interaction s policy dataplane-om; podporovaný cluster má probes k Pode umožniť podľa svojej networking implementácie. Pri probléme zachovaj source/destination flow a policy verdict.

## 10. HorizontalPodAutoscaler

Vytvor `hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payments-api
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payments-api
  minReplicas: 6
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
  behavior:
    scaleUp:
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
        - type: Percent
          value: 50
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
```

HPA vyžaduje resource metrics pipeline. Ak metrics-server alebo ekvivalent nie je dostupný, workload môže bežať, ale HPA nebude mať aktívny metric. Deployment requests tvoria denominator CPU utilization, preto ich zmena vyžaduje HPA revalidation.

HPA môže meniť replicas nad šesť. Verification script preto nepredpokladá vždy presne šesť Podov; porovnáva desired a ready state.

## 11. Kustomization

Vytvor `kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - serviceaccount.yaml
  - configmap.yaml
  - deployment.yaml
  - service.yaml
  - pdb.yaml
  - networkpolicy.yaml
  - hpa.yaml
commonLabels:
  app.kubernetes.io/managed-by: atlas-kustomize
```

Secret vzor nie je medzi resources. Pred apply musí Secret existovať z externého flowu.

`commonLabels` doplní management label. Pri použití Kustomize transformerov vždy skontroluj rendered selectors; plošné label transformácie môžu meniť selector semantics podľa verzie a configuration.

## 12. Broken selector overlay

Vytvor `overlays/broken-selector/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../..
patches:
  - target:
      group: ""
      version: v1
      kind: Service
      name: payments-api
    patch: |-
      - op: replace
        path: /spec/selector/app.kubernetes.io~1name
        value: payments-api-broken
```

JSON Patch path escapuje `/` v label key ako `~1`. Overlay zmení iba Service selector. Deployment a Pods zostanú zdravé, ale EndpointSlice pre Service stratí matching backends.

## 13. Broken readiness overlay

Vytvor `overlays/broken-readiness/kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../..
patches:
  - target:
      group: apps
      version: v1
      kind: Deployment
      name: payments-api
    patch: |-
      - op: replace
        path: /spec/template/spec/containers/0/readinessProbe/httpGet/path
        value: /endpoint-that-does-not-exist
```

Táto zmena modifikuje Pod template, preto Deployment vytvorí nový ReplicaSet. Nové containers môžu byť `Running` a liveness môže byť zelená, ale readiness bude zlyhávať a rollout sa nedokončí.

## 14. Verification script

Vytvor `scripts/verify.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

namespace="${NAMESPACE:-production}"
deployment="payments-api"
service="payments-api"
verify_image="${VERIFY_IMAGE:?Set VERIFY_IMAGE to an immutable curl image digest}"

printf 'Context: %s\n' "$(kubectl config current-context)"
kubectl auth whoami

kubectl get secret payments-runtime-se08 \
  --namespace "$namespace" \
  -o jsonpath='secret={.metadata.name} uid={.metadata.uid}{"\n"}'

kubectl rollout status \
  "deployment/${deployment}" \
  --namespace "$namespace" \
  --timeout=10m

generation="$(
  kubectl get deployment "$deployment" \
    --namespace "$namespace" \
    -o jsonpath='{.metadata.generation}'
)"
observed="$(
  kubectl get deployment "$deployment" \
    --namespace "$namespace" \
    -o jsonpath='{.status.observedGeneration}'
)"
desired="$(
  kubectl get deployment "$deployment" \
    --namespace "$namespace" \
    -o jsonpath='{.spec.replicas}'
)"
ready="$(
  kubectl get deployment "$deployment" \
    --namespace "$namespace" \
    -o jsonpath='{.status.readyReplicas}'
)"

printf 'generation=%s observed=%s desired=%s ready=%s\n' \
  "$generation" "$observed" "$desired" "${ready:-0}"

test "$generation" = "$observed"
test "${ready:-0}" = "$desired"

kubectl get replicasets \
  --namespace "$namespace" \
  -l app.kubernetes.io/name=payments-api \
  -o wide

kubectl get pods \
  --namespace "$namespace" \
  -l app.kubernetes.io/name=payments-api \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,NODE:.spec.nodeName,HASH:.metadata.labels.pod-template-hash,READY:.status.containerStatuses[0].ready,IMAGE:.spec.containers[0].image,IMAGE_ID:.status.containerStatuses[0].imageID,CONFIG:.metadata.annotations.atlas\.example/config-generation'

ready_endpoints="$(
  kubectl get endpointslices \
    --namespace "$namespace" \
    -l kubernetes.io/service-name="$service" \
    -o json \
  | jq '[.items[].endpoints[]? | select(.conditions.ready == true)] | length'
)"

printf 'ready_endpoints=%s\n' "$ready_endpoints"
test "$ready_endpoints" -ge 1

verifier="payments-verifier-$(date +%s)"
cleanup() {
  kubectl delete pod "$verifier" \
    --namespace "$namespace" \
    --ignore-not-found \
    --wait=false >/dev/null 2>&1 || true
}
trap cleanup EXIT

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ${verifier}
  namespace: ${namespace}
  labels:
    access: payments-client
spec:
  restartPolicy: Never
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 65532
    runAsGroup: 65532
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: curl
      image: ${verify_image}
      command: ["curl"]
      args:
        - -fsS
        - http://${service}.${namespace}.svc/version
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
EOF

kubectl wait pod "$verifier" \
  --namespace "$namespace" \
  --for=jsonpath='{.status.phase}'=Succeeded \
  --timeout=120s

kubectl logs "$verifier" --namespace "$namespace"
```

Nastav executable bit:

```bash
chmod +x scripts/verify.sh
```

Script kontroluje controller generation, ready count, ReplicaSets, Pod runtime image IDs, ready EndpointSlice a Service request z Podu, ktorý má správny NetworkPolicy label. Nepreukazuje external Gateway, databázovú transakciu ani multi-zone failure recovery.

## 15. Render pred API serverom

Najprv vyrenderuj Kustomize model lokálne:

```bash
kubectl kustomize . > rendered.yaml
```

Skontroluj resources:

```bash
yq -r '.kind + "\t" + (.metadata.namespace // "-") + "/" + .metadata.name' \
  rendered.yaml
```

`kubectl kustomize` dokazuje lokálny render. Nevykonáva API defaulting, Pod Security Admission, webhook mutation ani schema kontrolu servera.

Vyhľadaj placeholder:

```bash
grep -n '<payments-api-digest>' rendered.yaml
```

Pred pokračovaním ho nahraď skutočným digestom v `deployment.yaml`. Rovnako si priprav immutable `VERIFY_IMAGE` digest pre curl image.

## 16. Server-side dry-run

```bash
kubectl apply \
  --server-side \
  --dry-run=server \
  --field-manager=atlas-kubernetes-walkthrough \
  -k . \
  -o yaml \
  > admitted-dry-run.yaml
```

Tento krok overí API discovery, schema, defaulting a admission vrátane Pod Security. Objekty neuloží a controllers sa nespustia.

Ak Secret ešte neexistuje, Deployment dry-run môže stále prejsť, pretože API server bežne nekontroluje existenciu každej runtime reference. Preto máme samostatný precondition:

```bash
kubectl get secret payments-runtime-se08 -n production
```

## 17. Diff

```bash
kubectl diff \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .
```

`kubectl diff` ukáže rozdiel medzi live a navrhovaným server-side modelom. Exit code môže rozlišovať no diff, diff a chybu; CI wrapper ho musí interpretovať správne.

Diff nepreukazuje runtime convergence. Je to pre-mutation evidence.

## 18. Apply

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .
```

API success znamená, že objekty boli prijaté. Teraz controllers začnú vytvárať ReplicaSet, Pods, EndpointSlice a HPA status.

## 19. Sleduj object graph

```bash
kubectl get deployment payments-api -n production -o wide
kubectl get replicasets -n production -l app.kubernetes.io/name=payments-api -o wide
kubectl get pods -n production -l app.kubernetes.io/name=payments-api -o wide
```

Ak Deployment existuje, ale ReplicaSet nie, problém je pred Pod creation. Ak Pods existujú bez Node assignmentu, problém je scheduling. Ak sú assigned, ale `ContainerCreating`, presuň sa na image/CNI/volume Node boundary.

Sleduj rollout:

```bash
kubectl rollout status deployment/payments-api \
  --namespace production \
  --timeout=10m
```

Po úspechu spusti verification:

```bash
export VERIFY_IMAGE='curlimages/curl@sha256:<curl-image-digest>'
./scripts/verify.sh
```

## 20. Read-back effective runtime-u

Deployment source image:

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

Pod runtime image IDs:

```bash
kubectl get pods -n production \
  -l app.kubernetes.io/name=payments-api \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

Template security:

```bash
kubectl get deployment payments-api -n production -o json \
  | jq '.spec.template.spec | {
      serviceAccountName,
      automountServiceAccountToken,
      securityContext,
      containerSecurityContext: .containers[0].securityContext,
      resources: .containers[0].resources
    }'
```

Pod template dokazuje configured security intent. Runtime proof môže vyžadovať Node/runtime introspection alebo application self-report. Restricted admission je ďalší, nie konečný, dôkaz.

EndpointSlice:

```bash
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Každý ready endpoint má ukazovať na aktuálny Pod UID. Service request z verification Podu overí DNS, NetworkPolicy, Service translation a application endpoint.

## 21. Druhý nezmenený apply

Zaznamenaj ReplicaSet UIDs a Deployment generation:

```bash
before_generation="$(
  kubectl get deployment payments-api -n production \
    -o jsonpath='{.metadata.generation}'
)"

before_rs="$(
  kubectl get rs -n production \
    -l app.kubernetes.io/name=payments-api \
    -o jsonpath='{range .items[*]}{.metadata.uid}{"\n"}{end}' \
  | sort
)"
```

Znovu aplikuj rovnaký source:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .
```

Porovnaj:

```bash
after_generation="$(
  kubectl get deployment payments-api -n production \
    -o jsonpath='{.metadata.generation}'
)"

after_rs="$(
  kubectl get rs -n production \
    -l app.kubernetes.io/name=payments-api \
    -o jsonpath='{range .items[*]}{.metadata.uid}{"\n"}{end}' \
  | sort
)"

test "$before_generation" = "$after_generation"
test "$before_rs" = "$after_rs"
```

Nezmenený apply nemá vytvoriť novú Deployment generation ani ReplicaSet. Managed fields alebo resourceVersion sa môžu meniť podľa operation detailov; release identity zostáva rovnaká.

## 22. Configuration update `C53`

V `configmap.yaml` zmeň:

```yaml
CONFIG_GENERATION: "C53"
```

V `deployment.yaml` zmeň annotation:

```yaml
atlas.example/config-generation: "C53"
```

Najprv diff:

```bash
kubectl diff \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .
```

Potom apply a rollout:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .

kubectl rollout status deployment/payments-api \
  -n production \
  --timeout=10m
```

Zmena ConfigMap source-u aktualizuje objekt. Annotation zmení Pod template, vytvorí nový ReplicaSet a nové Pods načítajú environment `C53` pri štarte.

Over:

```bash
kubectl get rs -n production \
  -l app.kubernetes.io/name=payments-api -o wide

kubectl get pods -n production \
  -l app.kubernetes.io/name=payments-api \
  -o custom-columns='NAME:.metadata.name,HASH:.metadata.labels.pod-template-hash,CONFIG:.metadata.annotations.atlas\.example/config-generation,READY:.status.containerStatuses[0].ready'

./scripts/verify.sh
```

## 23. Recreate jedného Podu

Vyber jeden Ready Pod:

```bash
pod="$(
  kubectl get pods -n production \
    -l app.kubernetes.io/name=payments-api \
    -o jsonpath='{.items[0].metadata.name}'
)"

old_uid="$(kubectl get pod "$pod" -n production -o jsonpath='{.metadata.uid}')"
kubectl delete pod "$pod" -n production
```

ReplicaSet vytvorí replacement. Po rollout stabilization:

```bash
kubectl rollout status deployment/payments-api -n production --timeout=10m
kubectl get pods -n production -l app.kubernetes.io/name=payments-api -o wide
./scripts/verify.sh
```

Nový Pod má nový UID a pravdepodobne inú IP. Deployment/ReplicaSet revision, image digest a config generation ostávajú rovnaké. `emptyDir` dáta starého Podu sú preč; walkthrough ich nepovažuje za durable business state.

## 24. Failure path: Service selector bez endpointov

Aplikuj broken selector overlay:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k overlays/broken-selector
```

Deployment Pods zostanú Ready:

```bash
kubectl get pods -n production \
  -l app.kubernetes.io/name=payments-api
```

Service selector je však nesprávny:

```bash
kubectl get service payments-api -n production -o yaml
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Verification zlyhá na `ready_endpoints` alebo Service requeste. Failure chain:

```text
application Pods sú healthy
→ Service selector nevyberie žiadny Pod
→ EndpointSlice nemá ready backends
→ ClusterIP request nemá destination
```

Kubelet, image ani readiness nie sú root cause.

Recovery:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .

./scripts/verify.sh
```

Over nielen Service request, ale aj to, že EndpointSlice targetRefs patria správnym Pod UIDs.

## 25. Failure path: Running, ale NotReady

Aplikuj broken readiness overlay:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k overlays/broken-readiness
```

Sleduj rollout:

```bash
kubectl rollout status deployment/payments-api \
  -n production \
  --timeout=2m || true
```

Nový ReplicaSet vytvorí Pods. Containers môžu byť Running a liveness `/healthz` môže prechádzať, no readiness path vracia 404.

```bash
kubectl get deployment,replicasets,pods -n production \
  -l app.kubernetes.io/name=payments-api -o wide

kubectl describe pod -n production <new-pod-name>
kubectl logs -n production <new-pod-name> -c api
```

Deployment môže zachovať časť starej ready capacity podľa `maxUnavailable`. Nová revision však nenahradí starú.

Failure chain:

```text
Pod scheduled
→ process Running
→ liveness green
→ readiness HTTP 404
→ Pod Ready=False
→ new endpoint nie je eligible
→ rollout nerobí progress
```

Recovery aplikovaním authoritative base:

```bash
kubectl apply \
  --server-side \
  --field-manager=atlas-kubernetes-walkthrough \
  -k .

kubectl rollout status deployment/payments-api \
  -n production \
  --timeout=10m

./scripts/verify.sh
```

Recovery sa neuzatvára iba stavom Running. Musí prejsť readiness, EndpointSlice a Service request.

## 26. HPA observation

```bash
kubectl get hpa payments-api -n production
kubectl describe hpa payments-api -n production
```

Ak resource metrics pipeline neexistuje, HPA condition môže ukázať metric error. Deployment a Service môžu stále fungovať na `minReplicas`. V produkcii je to degraded autoscaling capability a potrebuje alert.

Nevytváraj umelý CPU load v production clustri bez guardrails. V lab-e možno použiť bounded load generator a sledovať celý chain:

```text
metric rastie
→ HPA desired replicas
→ Deployment scale
→ nové Pods
→ scheduler/Nodes
→ readiness
→ Service capacity
```

## 27. Forbidden security test

Skús server-side dry-run privileged Podu v Restricted namespace:

```bash
cat <<'EOF' \
  | kubectl apply --dry-run=server -f -
apiVersion: v1
kind: Pod
metadata:
  name: forbidden-privileged
  namespace: production
spec:
  containers:
    - name: shell
      image: busybox:1.36
      securityContext:
        privileged: true
EOF
```

Očakávaj admission rejection. Test nič nevytvorí. Ak prejde, namespace policy alebo exemption nezodpovedá očakávaniu a walkthrough nemá pokračovať s tvrdením, že Restricted policy je enforced.

Forbidden test musí používať schválený non-sensitive image reference v reálnom prostredí; placeholder tag v tomto príklade je iba payload pre admission a container sa pri dry-run nespustí.

## 28. Evidence pred cleanupom

Pred odstránením ulož:

```bash
mkdir -p evidence

kubectl get deployment,replicasets,pods,service,endpointslices,hpa,pdb,networkpolicy \
  -n production \
  -o yaml \
  > evidence/runtime-objects.yaml

kubectl get events -n production --sort-by=.lastTimestamp \
  > evidence/events.txt

kubectl get deployment payments-api -n production -o json \
  > evidence/deployment.json
```

Pri reálnom incidente by sa doplnili logs, audit, Node/runtime, CNI a metrics podľa symptómu. Snapshot všetkého bez otázky nie je náhrada causal diagnosis, ale destructive cleanup nemá odstrániť jediný dostupný dôkaz.

## 29. Cleanup

Najprv odstráň resources z Kustomize modelu:

```bash
kubectl delete -k .
```

Secret bol vytvorený mimo Kustomize a odstráni sa osobitne:

```bash
kubectl delete secret payments-runtime-se08 -n production
```

Nakoniec Namespace:

```bash
kubectl delete namespace production
```

V shared clustri nepoužívaj production namespace pre lab. Zvoľ samostatný názov a uprav manifests. Delete Namespace odstráni namespaced Kubernetes objekty, ale external cloud resources, retained PVs, logs a secret targets môžu mať samostatný lifecycle.

## 30. Čo walkthrough dokázal

Po úspešnom prechode máme evidence, že:

```text
Kustomize vyrenderoval očakávané objects
API a admission prijali restricted workload
Deployment vytvoril ReplicaSet a Pods
scheduler a Nodes realizovali runtime
image digest a imageID sú čitateľné
readiness vytvorila ready EndpointSlice
NetworkPolicy dovolila označený verifier path
Service request dosiahol application endpoint
nezmenený apply nevytvoril novú revision
config generation vytvorila controlled rollout
Pod replacement zachoval controller/release contract
broken selector a broken readiness boli diagnostikovateľné
forbidden privileged Pod bol odmietnutý
```

Walkthrough nepreukázal:

```text
external Gateway alebo internet path
production database a exactly-once payment commit
multi-zone survivability pri strate zone
persistent storage backup/restore
cluster upgrade alebo etcd recovery
reálne HPA scale pod reprezentatívnym loadom
```

Tieto outcomes potrebujú samostatné testy a prostredie.

## Referencie

- [Declarative Management of Kubernetes Objects Using Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/)
- [Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
