# Praktický GitOps projekt od Git revision po overený runtime

Táto kapitola vytvorí malý, ale úplný GitOps flow na lokálnom Kubernetes clustri. Git repository bude vlastniť environment intent, Argo CD bude jediným writerom Git-owned fields a výsledok sa overí v štyroch odlišných vrstvách: resolved Git revision, rendered desired state, live Kubernetes generation a aplikačný outcome.

Walkthrough nepovažuje `Synced` alebo `Healthy` za konečný dôkaz. Tie hovoria o Argo CD comparison a health modeloch. Release sa uzatvorí až vtedy, keď live Deployment používa očakávaný image digest, Pody načítali správnu configuration generation, Service má eligible endpoints a reálny request vráti očakávanú release identity.

```text
versionovaný environment source
→ reviewed Git commit
→ Argo CD source resolution
→ Kustomize render
→ desired/live comparison
→ Kubernetes apply a reconciliation
→ serving Pod cohort
→ version a business request
→ drift/self-heal alebo Git recovery
```

## Predpoklady a bezpečnostná hranica

Lab vyžaduje Docker alebo kompatibilný container runtime, `kind`, `kubectl`, `git`, `argocd`, `curl` a `jq`. Používa lokálny cluster `gitops-lab`, no Git repository musí byť dostupné Argo CD repo-serveru. Najjednoduchší lab používa dočasné verejné repository bez secretov. Private repository potrebuje samostatný repository credential contract; nepridávaj osobný token priamo do Application manifestu.

Použité toolchain identity sú explicitné:

```bash
export KIND_VERSION='v0.31.0'
export KIND_NODE='kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f'
export ARGOCD_VERSION='v3.4.2'
export GIT_REPO_URL='https://github.com/EXAMPLE/atlas-gitops-lab.git'
export APP_IMAGE='registry.example.com/atlas/payments-api@sha256:REPLACE_WITH_REAL_DIGEST'
```

`APP_IMAGE` musí byť skutočný multi-platform alebo host-compatible digest. Walkthrough nevytvára application image; používa artifact z Docker/CI kapitoly. Mutable tag by oslabil väzbu medzi schváleným release-om a runtime bytes.

Over binaries:

```bash
kind version
kubectl version --client
argocd version --client
```

Tool version output nepreukazuje, že cluster alebo Argo control plane používa rovnakú generation. Tie sa read-backnú po inštalácii.

## 1. Vytvorenie pinned kind clusteru

```bash
kind create cluster \
  --name gitops-lab \
  --image "$KIND_NODE" \
  --wait 120s

kubectl cluster-info --context kind-gitops-lab
kubectl get nodes -o wide
```

`kind create cluster` vytvorí Kubernetes node ako container. Digest pin chráni node-image bytes; nepreukazuje host kernel alebo Docker runtime. `kubectl get nodes` potvrdí API a node registration, nie application readiness.

Zachovaj cluster identity:

```bash
kubectl config current-context
kubectl get namespace kube-system -o jsonpath='{.metadata.uid}{"\n"}'
```

Namespace UID pomáha odlíšiť novo vytvorený cluster od starého clusteru s rovnakým context name.

## 2. Inštalácia Argo CD z pinned release manifestu

```bash
kubectl create namespace argocd
kubectl apply --server-side --force-conflicts \
  -n argocd \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"

kubectl -n argocd rollout status deployment/argocd-server --timeout=180s
kubectl -n argocd rollout status deployment/argocd-repo-server --timeout=180s
kubectl -n argocd rollout status statefulset/argocd-application-controller --timeout=180s
```

Pinned release URL je lepší než mutable `stable`, ale download stále prechádza sieťou. Produkčný bootstrap má mirrorovať a overovať manifest alebo používať schválený package digest. Server-side apply s force-conflicts je vhodný pre upstream install manifest podľa release quick startu; nemá sa mechanicky kopírovať na application resources bez ownership analýzy.

Read-back controller images:

```bash
kubectl -n argocd get deploy,statefulset -o json | jq -r '
  .items[] |
  .metadata.name as $name |
  .spec.template.spec.containers[] |
  [$name,.name,.image] | @tsv
'
```

Tento výstup ukáže image references v Pod templates. Running container IDs a resolved digests možno čítať z Pod statusu.

CLI použije core mode, takže netreba publikovať Argo API server ani pracovať s admin heslom:

```bash
argocd login --core
argocd version
```

Core mode vykonáva operácie cez Kubernetes API a current kubeconfig. To zároveň znamená, že local user potrebuje zodpovedajúce Kubernetes oprávnenia.

## 3. Environment repository

V prázdnom lokálnom clone vytvor:

```text
atlas-gitops-lab/
├── platform/
│   ├── app-project.yaml
│   └── application.yaml
└── environments/
    └── lab/
        ├── kustomization.yaml
        ├── namespace.yaml
        ├── configmap.yaml
        ├── deployment.yaml
        └── service.yaml
```

`environments/lab/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: payments-lab
  labels:
    atlas.example/environment: lab
```

`configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payments-release
  namespace: payments-lab
data:
  RELEASE_ID: release-001
  POLICY_GENERATION: "1842"
```

`deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: payments-lab
  labels:
    app.kubernetes.io/name: payments-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
    spec:
      containers:
        - name: api
          image: registry.example.invalid/replace-me@sha256:replace-me
          imagePullPolicy: IfNotPresent
          envFrom:
            - configMapRef:
                name: payments-release
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 3
            failureThreshold: 20
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 10
          resources:
            requests:
              cpu: 20m
              memory: 32Mi
            limits:
              memory: 128Mi
```

`service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
  namespace: payments-lab
spec:
  selector:
    app.kubernetes.io/name: payments-api
  ports:
    - name: http
      port: 80
      targetPort: http
```

`kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
  - configmap.yaml
  - deployment.yaml
  - service.yaml
images:
  - name: registry.example.invalid/replace-me
    newName: registry.example.com/atlas/payments-api
    digest: sha256:REPLACE_WITH_REAL_DIGEST
commonLabels:
  atlas.example/managed-by: argocd
```

Nahraď repository host a digest zo `$APP_IMAGE`. `kustomize build` musí ešte pred commitom ukázať exact image:

```bash
kubectl kustomize environments/lab > /tmp/rendered.yaml
grep -n 'image:' /tmp/rendered.yaml
kubectl apply --dry-run=server -f /tmp/rendered.yaml
```

Local render kontroluje Kustomize semantics. Server dry-run kontroluje current Kubernetes API a admission. Ani jedno nevykoná Argo comparison alebo runtime rollout.

## 4. AppProject ako policy boundary

`platform/app-project.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments
  namespace: argocd
spec:
  description: Payments lab applications
  sourceRepos:
    - https://github.com/EXAMPLE/atlas-gitops-lab.git
  destinations:
    - namespace: payments-lab
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - group: ""
      kind: Namespace
  namespaceResourceWhitelist:
    - group: ""
      kind: ConfigMap
    - group: ""
      kind: Service
    - group: apps
      kind: Deployment
```

Project zúži source, destination a resource kinds. Nie je network policy ani image-admission policy. Application stále môže odkázať na nevhodný digest, ak ďalšia policy vrstva image contract neoverí.

Aplikuj project bootstrapom:

```bash
kubectl apply -f platform/app-project.yaml
```

Platform bootstrap je samostatná authority hranica. V produkcii má byť AppProject tiež spravovaný versionovaným platform GitOps flowom; lokálny lab ho aplikuje ručne, aby sa vyhol bootstrap circularity.

## 5. Application a automated reconciliation

`platform/application.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payments-lab
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: payments
  source:
    repoURL: https://github.com/EXAMPLE/atlas-gitops-lab.git
    targetRevision: main
    path: environments/lab
  destination:
    server: https://kubernetes.default.svc
    namespace: payments-lab
  syncPolicy:
    automated:
      enabled: true
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=false
      - PruneLast=true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 1m
```

`targetRevision: main` je mutable selector. Argo status musí preto zachovať resolved commit SHA. Produkčný promotion môže namiesto branch-e používať immutable tag alebo exact commit, no potom treba explicitne meniť Application source. Tento lab demonštruje continuous reconciliation nad protected environment branchom.

Commit a push:

```bash
git add .
git commit -m 'add payments lab desired state'
git push origin main
export DESIRED_REVISION=$(git rev-parse HEAD)
```

Potom aplikuj Application:

```bash
kubectl apply -f platform/application.yaml
argocd app wait payments-lab --sync --health --timeout 300
```

## 6. Resolved desired a live state

Argo read-back:

```bash
argocd app get payments-lab --hard-refresh
kubectl -n argocd get application payments-lab -o json > /tmp/application.json
jq '{
  targetRevision:.spec.source.targetRevision,
  resolvedRevision:.status.sync.revision,
  sync:.status.sync.status,
  health:.status.health.status,
  operation:.status.operationState.phase
}' /tmp/application.json
```

Porovnaj resolved revision:

```bash
actual_revision=$(jq -r '.status.sync.revision' /tmp/application.json)
[[ "$actual_revision" == "$DESIRED_REVISION" ]]
```

`Synced` znamená, že Argo comparison pre tracked resources nenašlo relevantný desired/live rozdiel podľa current rules. `Healthy` je agregovaný health verdict. Obe labels musia byť viazané na resolved revision a doplnené live read-backom.

```bash
kubectl -n payments-lab get deployment payments-api -o json | jq '{
  generation:.metadata.generation,
  observed:.status.observedGeneration,
  desiredImage:.spec.template.spec.containers[0].image,
  replicas:.status.replicas,
  ready:.status.readyReplicas,
  available:.status.availableReplicas
}'

kubectl -n payments-lab get pods -l app.kubernetes.io/name=payments-api -o json | jq -r '
  .items[] |
  [.metadata.name,
   .metadata.uid,
   .spec.containers[0].image,
   .status.containerStatuses[0].imageID,
   .status.conditions[]? | select(.type=="Ready") | .status] | @tsv
'

kubectl -n payments-lab get endpointslice \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Pod `imageID` je runtime-resolved identity. Service endpoint readiness ukazuje serving eligibility, nie HTTP alebo business correctness.

## 7. Aplikačný read-back

Spusť port-forward:

```bash
kubectl -n payments-lab port-forward service/payments-api 18080:80 >/tmp/payments-port-forward.log 2>&1 &
PF_PID=$!
trap 'kill "$PF_PID" 2>/dev/null || true' EXIT
sleep 2
```

Over endpoints:

```bash
curl --fail --silent http://127.0.0.1:18080/version | jq .
curl --fail --silent http://127.0.0.1:18080/readyz
```

Očakávaj image/source version a `RELEASE_ID=release-001`, `POLICY_GENERATION=1842` podľa contractu aplikácie. Ak `/version` tieto fields neposkytuje, doplň ho v application artifacte; bez loaded-generation endpointu GitOps nevie nezávisle preukázať process state.

Business test použije idempotency identity podľa API z predchádzajúcich sekcií:

```bash
curl --fail --silent \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: gitops-lab-001' \
  --data '{"amount":500,"currency":"EUR"}' \
  http://127.0.0.1:18080/v1/payments | tee /tmp/payment-first.json

curl --fail --silent \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: gitops-lab-001' \
  --data '{"amount":500,"currency":"EUR"}' \
  http://127.0.0.1:18080/v1/payments | tee /tmp/payment-retry.json

diff -u /tmp/payment-first.json /tmp/payment-retry.json
```

Dve rovnaké responses podporujú idempotency oracle. Úplný dôkaz môže vyžadovať ledger alebo audit count, pretože rovnaká response sa dá vrátiť aj po duplicate side effecte.

## 8. Druhý Git release

Zmeň ConfigMap na `release-002` a image digest na nový schválený artifact. Pred pushom:

```bash
kubectl kustomize environments/lab > /tmp/release-002.yaml
kubectl apply --dry-run=server -f /tmp/release-002.yaml

git add environments/lab
git commit -m 'promote payments release-002'
git push origin main
export DESIRED_REVISION_2=$(git rev-parse HEAD)
```

Wait a read-back:

```bash
argocd app wait payments-lab --sync --health --timeout 300
kubectl -n argocd get application payments-lab -o jsonpath='{.status.sync.revision}{"\n"}'
kubectl -n payments-lab rollout status deployment/payments-api --timeout=180s
```

Potom opakuj imageID, `/version` a business probe s novou operation identity. Git commit success nie je release success; controller a business evidence musia patriť `DESIRED_REVISION_2`.

## 9. Failure: manuálny drift a self-heal

Zmeň live replicas mimo Git-u:

```bash
kubectl -n payments-lab scale deployment/payments-api --replicas=5
kubectl -n payments-lab get deployment payments-api -o jsonpath='{.spec.replicas}{"\n"}'
```

Argo má pri `selfHeal: true` drift zistiť a vrátiť replicas na Git value 2. Sleduj:

```bash
argocd app get payments-lab --refresh
kubectl -n argocd get application payments-lab -w
kubectl -n payments-lab get deployment payments-api -w
```

Ak HPA legitímne vlastní replicas, Git nemá súčasne vlastniť fixnú hodnotu. Tento lab HPA nepoužíva, takže manual scale je unauthorized drift. V produkcii sa ownership klasifikuje podľa field managera a designu; self-heal nemá slepo prepisovať delegated controller state.

Po self-heal over:

```bash
kubectl -n payments-lab get deployment payments-api \
  -o jsonpath='{.spec.replicas}{" "}{.status.readyReplicas}{"\n"}'
argocd app get payments-lab
```

## 10. Failure: chybný image digest

Commitni neexistujúci digest alebo repository a pushni. Argo môže byť `Synced`, pretože desired spec bola aplikovaná, ale health bude degraded/progressing a Pody skončia `ImagePullBackOff`.

Evidence:

```bash
kubectl -n payments-lab get pods -o wide
kubectl -n payments-lab describe pod -l app.kubernetes.io/name=payments-api
kubectl -n payments-lab get events --sort-by=.lastTimestamp | tail -30
argocd app get payments-lab
```

Recovery sa vykoná Git revertom alebo novým commitom na known-good digest:

```bash
git revert --no-edit HEAD
git push origin main
argocd app wait payments-lab --sync --health --timeout 300
```

Pri automated sync sa nespoliehaj na ad-hoc Argo rollback ako trvalý desired state. Git musí znovu reprezentovať autoritatívnu recovery generation. Po recovery over resolved revision, live imageID, `/version` a business operation.

## 11. Failure: resource zmizne z Git-u a prune

Odstránenie Service z `kustomization.yaml` spôsobí, že s `prune: true` sa stane extraneous a po syncu sa odstráni. Pred takým change používaj render diff a explicitný review. Kritické resources môžu používať `Prune=confirm` alebo iný platform guardrail.

V lab-e možno vytvoriť temporary ConfigMap, commitnúť, počkať na sync, potom ho odstrániť z Git-u a sledovať prune. Po každom kroku porovnaj Argo resource inventory a live object UID.

Prune success nie je business recovery. Ak Service zmizne, application Pody môžu zostať healthy, ale user path zlyhá. Acceptance musí zahŕňať routing probe.

## 12. Troubleshooting artifacts

Pri každom zlyhaní zachovaj:

```bash
kubectl -n argocd get application payments-lab -o yaml > /tmp/application.yaml
argocd app manifests payments-lab > /tmp/argocd-manifests.yaml
argocd app diff payments-lab > /tmp/argocd-diff.txt || true
kubectl -n payments-lab get all,configmap,endpointslice -o yaml > /tmp/live.yaml
kubectl -n payments-lab get events --sort-by=.lastTimestamp > /tmp/events.txt
```

Manifest command ukazuje controller-resolved desired output pre Application. Live dump ukazuje Kubernetes objects. Ani jeden neukazuje process-loaded state alebo external business ledger.

## Cleanup

Najprv odstráň Application a počkaj na finalizer/prune:

```bash
kubectl -n argocd delete application payments-lab
kubectl wait --for=delete namespace/payments-lab --timeout=180s || true
kind delete cluster --name gitops-lab
```

Ak Application deletion visí, neodstraňuj finalizer naslepo. Skontroluj resources, destination availability, controller logs a deletion policy. Force removal môže orphanovať resources.

Dočasné remote Git repository odstráň podľa jeho hosting policy. Zruš deploy keys alebo tokens, ak boli použité.

## Acceptance walkthroughu

Walkthrough je úspešný, keď:

```text
kind node a Argo CD release sú pinned
AppProject obmedzuje source, destination a kinds
Application source sa resolve-ne na očakávaný commit
render a server dry-run prejdú
Argo desired/live comparison je Synced
Deployment observedGeneration dobehne generation
Pody používajú očakávaný runtime imageID
Service má ready endpoints
/version hlási artifact a config generation
business retry nevytvorí duplicate outcome
manual Git-owned drift sa self-healne
git revert obnoví chybný image release
prune a deletion majú explicitnú safety hranicu
cleanup odstráni Application resources aj cluster
```

Lab tým demonštruje GitOps ako authority a reconciliation system. Git commit, Argo status, Kubernetes readiness a business outcome zostávajú samostatné, korelované dôkazy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Multi-tenancy](multi-tenancy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: GitOps troubleshooting →](gitops-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
