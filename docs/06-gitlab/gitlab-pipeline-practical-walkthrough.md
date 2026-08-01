# Praktický GitLab pipeline od source change po overený deployment

Táto kapitola materializuje pojmy zo sekcie GitLab do jedného súvislého príkladu. Nejde o katalóg samostatných YAML fragmentov. Vytvoríme konkrétny pipeline pre službu `payments-api` a prejdeme celý tok:

```text
source change
→ merge-request pipeline
→ test a report evidence
→ trusted image build
→ immutable registry digest
→ image security scan
→ staging deployment
→ Kubernetes rollout
→ live-image read-back
→ service smoke test
→ manuálne povolený production deployment
```

Pri každom súbore a príkaze rozlíšime, čo je iba deklarácia, čo GitLab skutočne resolve-ne do pipeline graphu, čo vykoná runner, čo sa uloží ako artifact alebo deployment record a čo musí byť ešte nezávisle overené v Kubernetes a na aplikačnej vrstve.

Príklad používa GitLab Container Registry a Kubernetes cluster pripojený cez GitLab agent context. Konkrétne image verzie a digesty v ukážke treba v reálnom repository nahradiť organizáciou schválenými a overenými digestmi.

## 1. Výsledná štruktúra repository

Budeme pracovať s týmto minimálnym projektom:

```text
payments-api/
├── .gitlab-ci.yml
├── Dockerfile
├── package.json
├── package-lock.json
├── src/
│   └── server.js
├── test/
│   └── server.test.js
├── scripts/
│   └── verify-deployment.sh
└── deploy/
    ├── deployment.yaml
    └── service.yaml
```

Source tree nie je pipeline ani release. Pipeline subject vznikne až kombináciou konkrétneho commit SHA, pipeline source, effective `.gitlab-ci.yml`, všetkých includes, project/group variables, runner class a GitLab platform generation. Deployment navyše pridá image digest, cluster context, namespace a live resource generation.

## 2. Malá aplikácia a jej runtime contract

`src/server.js` môže byť jednoduchá HTTP služba:

```javascript
import http from "node:http";

const port = Number(process.env.PORT ?? 8080);
const version = process.env.APP_VERSION ?? "dev";
const commit = process.env.APP_COMMIT ?? "unknown";

const server = http.createServer((request, response) => {
  if (request.url === "/readyz") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ ready: true, version, commit }));
    return;
  }

  if (request.url === "/version") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ service: "payments-api", version, commit }));
    return;
  }

  response.writeHead(404);
  response.end();
});

server.listen(port, "0.0.0.0");
```

Endpoint `/readyz` je process-level readiness oracle. Dokazuje, že tento proces prijal HTTP request a vrátil očakávaný payload. Nedokazuje funkčnosť databázy, message brokera ani celého payment journey. `/version` nám neskôr umožní overiť, že traffic spracúva očakávaný commit.

Relevantná časť `package.json`:

```json
{
  "name": "payments-api",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node src/server.js",
    "lint": "eslint src test",
    "test:ci": "node --test --test-reporter=junit --test-reporter-destination=reports/junit.xml"
  },
  "engines": {
    "node": ">=22"
  }
}
```

Pipeline bude očakávať report `reports/junit.xml`. Zelený `npm test` bez report artifactu nie je complete GitLab test evidence, ak merge gate alebo audit očakáva machine-readable report.

## 3. `Dockerfile`: jeden image artifact pre ďalšie prostredia

Vytvor `Dockerfile`:

```dockerfile
FROM node:22.14.0-alpine@sha256:<verified-node-base-digest> AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:22.14.0-alpine@sha256:<verified-node-base-digest> AS runtime
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080

COPY --from=dependencies /app/node_modules ./node_modules
COPY package.json ./package.json
COPY src ./src

USER node
EXPOSE 8080
CMD ["node", "src/server.js"]
```

Dve stages oddeľujú dependency installation od runtime image-u. `npm ci` používa lockfile a odmietne nezhodu medzi `package.json` a `package-lock.json`. Pinned base-image digest znižuje riziko, že rovnaký source commit o deň neskôr vytvorí iné bytes.

Ani digest-pinned base image však automaticky nedokazuje jeho dôveryhodný pôvod alebo absenciu zraniteľností. Na to potrebujeme registry policy, provenance a scan nad výsledným digestom.

## 4. Kubernetes Deployment template

`deploy/deployment.yaml` obsahuje explicitné placeholdery, ktoré pipeline nahradí exact image digestom a commit SHA:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  labels:
    app.kubernetes.io/name: payments-api
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
      annotations:
        atlas.example/source-commit: "__COMMIT_SHA__"
    spec:
      containers:
        - name: payments-api
          image: "__IMAGE_REFERENCE__"
          imagePullPolicy: IfNotPresent
          env:
            - name: APP_VERSION
              value: "__APP_VERSION__"
            - name: APP_COMMIT
              value: "__COMMIT_SHA__"
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 15
            periodSeconds: 10
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

`__IMAGE_REFERENCE__` bude mať tvar:

```text
registry.example/atlas/payments-api@sha256:...
```

Použitie digestu je zásadné. Tag `$CI_COMMIT_SHA` je užitočný index alebo ľudský alias, ale registry tag môže byť pri nesprávnej policy prepísaný. Kubernetes Pod spec s digestom viaže rollout na konkrétny image manifest.

Service v `deploy/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payments-api
spec:
  selector:
    app.kubernetes.io/name: payments-api
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

Service selector dokazuje iba deklarovaný výber Podov. Až EndpointSlice read-back a reálny request ukážu, či má Service ready backendy a či cez ne prejde traffic.

## 5. Pipeline contract pred samotným YAML-om

Pipeline chceme rozdeliť na dva trust režimy.

Merge-request pipeline môže bezpečne pracovať s untrusted source z branch-e:

```text
lint
→ unit tests
→ JUnit report
→ žiadne registry write credentials
→ žiadny production runner
→ žiadny cluster access
```

Default-branch pipeline po merge-i môže vytvoriť release candidate:

```text
lint a tests
→ trusted image build
→ registry digest publication
→ scan presne toho digestu
→ staging deployment
→ runtime verification
→ manuálny production gate
```

Toto rozdelenie je dôležitejšie než názvy stages. Untrusted merge-request job nesmie byť schopný zmeniť vlastný script a následne použiť production credential alebo persistent privileged runner.

## 6. Kompletný `.gitlab-ci.yml`

Nasledujúci pipeline je zámerne v jednom súbore, aby bol resolved flow čitateľný. Neskôr ho možno rozdeliť do versionovaných includes, ale každé include pridá ďalšiu source a trust boundary.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never

stages:
  - validate
  - test
  - build
  - verify
  - deploy

variables:
  APP_NAME: payments-api
  APP_VERSION: "1.0.${CI_PIPELINE_IID}"
  IMAGE_TAG: "${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}"
  STAGING_NAMESPACE: payments-staging
  PRODUCTION_NAMESPACE: payments-production

# Default cache je vypnutá. Každý job ju musí povoliť vedome a s vhodným key.
default:
  interruptible: true
  cache: []
  retry:
    max: 1
    when:
      - runner_system_failure
      - stuck_or_timeout_failure

validate_source:
  stage: validate
  image: node:22.14.0-alpine@sha256:<verified-node-image-digest>
  script:
    - node --version
    - npm --version
    - npm ci
    - npm run lint
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

unit_tests:
  stage: test
  image: node:22.14.0-alpine@sha256:<verified-node-image-digest>
  needs:
    - job: validate_source
  script:
    - npm ci
    - mkdir -p reports
    - npm run test:ci
    - test -s reports/junit.xml
  artifacts:
    when: always
    expire_in: 14 days
    paths:
      - reports/junit.xml
    reports:
      junit: reports/junit.xml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

build_image:
  stage: build
  image: docker:27.5.1-cli@sha256:<verified-docker-cli-digest>
  services:
    - name: docker:27.5.1-dind@sha256:<verified-dind-digest>
      alias: docker
  tags:
    - trusted-build
  variables:
    DOCKER_HOST: tcp://docker:2376
    DOCKER_TLS_CERTDIR: /certs
    DOCKER_CERT_PATH: /certs/client
    DOCKER_TLS_VERIFY: "1"
  needs:
    - job: unit_tests
      artifacts: true
  before_script:
    - apk add --no-cache jq
    - echo "$CI_REGISTRY_PASSWORD" | docker login --username "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker buildx create --driver docker-container --use --name atlas-builder
    - >-
      docker buildx build
      --platform linux/amd64
      --provenance=true
      --sbom=true
      --tag "$IMAGE_TAG"
      --metadata-file build-metadata.json
      --push
      .
    - IMAGE_DIGEST="$(jq -er '."containerimage.digest"' build-metadata.json)"
    - test -n "$IMAGE_DIGEST"
    - printf 'IMAGE_DIGEST=%s\n' "$IMAGE_DIGEST" > build.env
    - printf 'IMAGE_REFERENCE=%s@%s\n' "$CI_REGISTRY_IMAGE" "$IMAGE_DIGEST" >> build.env
    - cat build.env
  artifacts:
    expire_in: 7 days
    paths:
      - build-metadata.json
    reports:
      dotenv: build.env
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

verify_registry_subject:
  stage: verify
  image: docker:27.5.1-cli@sha256:<verified-docker-cli-digest>
  services:
    - name: docker:27.5.1-dind@sha256:<verified-dind-digest>
      alias: docker
  tags:
    - trusted-build
  variables:
    DOCKER_HOST: tcp://docker:2376
    DOCKER_TLS_CERTDIR: /certs
    DOCKER_CERT_PATH: /certs/client
    DOCKER_TLS_VERIFY: "1"
  needs:
    - job: build_image
      artifacts: true
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login --username "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - test -n "$IMAGE_DIGEST"
    - docker buildx imagetools inspect "$IMAGE_REFERENCE"
    - RESOLVED_DIGEST="$(docker buildx imagetools inspect "$IMAGE_TAG" --format '{{json .Manifest.Digest}}' | tr -d '"')"
    - test "$RESOLVED_DIGEST" = "$IMAGE_DIGEST"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

scan_image:
  stage: verify
  image:
    name: aquasec/trivy:0.58.2@sha256:<verified-trivy-digest>
    entrypoint: [""]
  needs:
    - job: build_image
      artifacts: true
  script:
    - test -n "$IMAGE_REFERENCE"
    - >-
      trivy image
      --no-progress
      --format json
      --output trivy-image.json
      --severity HIGH,CRITICAL
      --exit-code 1
      "$IMAGE_REFERENCE"
    - test -s trivy-image.json
  artifacts:
    when: always
    expire_in: 30 days
    paths:
      - trivy-image.json
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

.deploy_template:
  stage: deploy
  image: alpine/k8s:1.35.0@sha256:<verified-kubectl-image-digest>
  needs:
    - job: build_image
      artifacts: true
    - job: verify_registry_subject
    - job: scan_image
  before_script:
    - test -n "$KUBE_CONTEXT"
    - test -n "$TARGET_NAMESPACE"
    - test -n "$IMAGE_REFERENCE"
    - kubectl config use-context "$KUBE_CONTEXT"
    - kubectl auth can-i patch deployment/payments-api --namespace "$TARGET_NAMESPACE"
  script:
    - mkdir -p rendered
    - >-
      sed
      -e "s|__IMAGE_REFERENCE__|${IMAGE_REFERENCE}|g"
      -e "s|__COMMIT_SHA__|${CI_COMMIT_SHA}|g"
      -e "s|__APP_VERSION__|${APP_VERSION}|g"
      deploy/deployment.yaml
      > rendered/deployment.yaml
    - cp deploy/service.yaml rendered/service.yaml
    - kubectl create namespace "$TARGET_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    - kubectl apply --server-side --dry-run=server --namespace "$TARGET_NAMESPACE" -f rendered/
    - kubectl apply --server-side --field-manager=gitlab-ci --namespace "$TARGET_NAMESPACE" -f rendered/
    - kubectl rollout status deployment/payments-api --namespace "$TARGET_NAMESPACE" --timeout=5m
    - LIVE_IMAGE="$(kubectl get deployment payments-api --namespace "$TARGET_NAMESPACE" -o jsonpath='{.spec.template.spec.containers[?(@.name=="payments-api")].image}')"
    - test "$LIVE_IMAGE" = "$IMAGE_REFERENCE"
    - kubectl get pods --namespace "$TARGET_NAMESPACE" -l app.kubernetes.io/name=payments-api -o wide
    - kubectl get endpointslice --namespace "$TARGET_NAMESPACE" -l kubernetes.io/service-name=payments-api -o yaml
    - >-
      kubectl run "payments-smoke-${CI_PIPELINE_ID}"
      --namespace "$TARGET_NAMESPACE"
      --rm --restart=Never --attach
      --image=curlimages/curl:8.12.1@sha256:<verified-curl-image-digest>
      --
      --fail --silent --show-error
      http://payments-api/version
  artifacts:
    when: always
    expire_in: 14 days
    paths:
      - rendered/

staging_deploy:
  extends: .deploy_template
  variables:
    TARGET_NAMESPACE: $STAGING_NAMESPACE
    KUBE_CONTEXT: atlas/platform-agent:staging
  environment:
    name: staging
    url: https://payments-staging.example.com
    deployment_tier: staging
  resource_group: payments-staging
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

production_deploy:
  extends: .deploy_template
  variables:
    TARGET_NAMESPACE: $PRODUCTION_NAMESPACE
    KUBE_CONTEXT: atlas/platform-agent:production
  environment:
    name: production
    url: https://payments.example.com
    deployment_tier: production
  resource_group: payments-production
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
      allow_failure: false
```

Nasledujúce časti rozoberajú, prečo je pipeline napísaný práve takto.

## 7. `workflow: rules`: ktorý pipeline vôbec vznikne

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

Tento blok rozhoduje o vytvorení celého pipeline-u. Prvá vetva povoľuje merge-request pipeline, druhá default-branch pipeline. Explicitné `when: never` odmietne ostatné events.

Bez takéhoto top-level rozhodnutia môže jeden push do branch-e s otvoreným merge requestom vytvoriť push aj merge-request pipeline. Dva pipelines potom nemusia mať rovnaký source subject ani rovnaké variables.

Úspešné vytvorenie pipeline-u preukazuje, že `workflow` pravidlá dovolili event. Nepreukazuje, že všetky očakávané jobs vznikli; každý job má ešte vlastné `rules`.

## 8. `needs`: dátový a execution graph

`unit_tests` deklaruje:

```yaml
needs:
  - job: validate_source
```

`build_image` deklaruje:

```yaml
needs:
  - job: unit_tests
    artifacts: true
```

`needs` nevytvára iba poradie. Pri artifacts-enabled edge určuje aj to, z ktorého producer jobu consumer stiahne výstupy. Pipeline stage môže byť vizuálne predchádzajúca, ale bez správneho artifact edge consumer nemusí dostať report alebo dotenv values, ktoré očakáva.

Dôveryhodný graph preto kontroluje:

```text
job existuje
→ predecessor existuje
→ predecessor patrí rovnakému pipeline subjectu
→ required artifact bol vytvorený
→ artifact nie je expired alebo neplatný
→ consumer ho skutočne načítal
```

## 9. JUnit report: test process verzus spracovaná evidence

`unit_tests` používa:

```yaml
artifacts:
  when: always
  reports:
    junit: reports/junit.xml
```

`when: always` zachová report aj pri test failure. To umožňuje diagnostiku a merge-request widget nemusí zostať bez evidence práve pri chybnom teste.

Príkaz:

```bash
test -s reports/junit.xml
```

preukazuje, že file existuje a nie je prázdny. Nepreukazuje, že je validný JUnit XML, že obsahuje všetky test suites alebo že GitLab report úspešne spracoval. Pipeline acceptance môže navyše porovnať expected test inventory s parsed reportom.

## 10. Trusted image build a runner boundary

Build job je obmedzený na default branch:

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

A používa runner tag:

```yaml
tags:
  - trusted-build
```

Runner s Docker-in-Docker alebo privileged executorom má vysoký host a supply-chain risk. Tag nie je bezpečnostná vlastnosť sám osebe. GitLab runner registration musí skutočne označovať protected a environment-appropriate runner a project nesmie dovoliť untrusted jobs používať ten istý tag.

Build vytvára jeden image a publikuje ho raz. Staging a production používajú rovnaký `IMAGE_REFERENCE`. Keby production job vykonal nový `docker build`, vznikol by nový artifact bez pôvodného test/scan subjectu.

## 11. Dotenv artifact ako bounded hand-off

Build job zapíše:

```text
IMAGE_DIGEST=sha256:...
IMAGE_REFERENCE=registry.example/atlas/payments-api@sha256:...
```

A publikuje ich:

```yaml
artifacts:
  reports:
    dotenv: build.env
```

GitLab načíta hodnoty do downstream jobov, ktoré získajú artifacts cez `needs`. Dotenv report je praktický hand-off malých non-secret metadata.

Do dotenv artifactu nepatrí registry password, cloud credential ani Vault token. Report artifact má retention, access a download surface; nie je secret manager.

## 12. Registry verification: tag a digest musia ukazovať na rovnaký subject

Build metadata poskytne digest. `verify_registry_subject` následne resolve-ne tag priamo z registry a porovná ho:

```bash
RESOLVED_DIGEST="$(docker buildx imagetools inspect "$IMAGE_TAG" --format '{{json .Manifest.Digest}}' | tr -d '"')"
test "$RESOLVED_DIGEST" = "$IMAGE_DIGEST"
```

Ak test prejde, v okamihu observation tag ukazoval na očakávaný digest. Nepreukazuje, že tag sa neskôr nedá prepísať. Produkčný Deployment preto používa digest reference, nie tag.

Pri multi-platform image treba navyše rozlíšiť OCI index digest od per-platform manifest digestov. Táto ukážka cieli iba `linux/amd64`; pri rozšírení na arm64 musí evidence inventory obsahovať oba platform subjects.

## 13. Scanner job a validita reportu

Scanner je viazaný na:

```bash
trivy image ... "$IMAGE_REFERENCE"
```

Nie na source directory ani mutable tag. Tým sa security verdict viaže na artifact, ktorý sa nasadzuje.

`--exit-code 1 --severity HIGH,CRITICAL` blokuje job pri matching findings podľa konkrétnej Trivy database a policy. Pri analyzer crashi alebo database download failure musí job skončiť ako tool failure, nie vytvoriť prázdny report a pokračovať.

`test -s trivy-image.json` overuje existenciu outputu. Silnejší gate musí ešte overiť JSON schema, scanner version, database freshness, target digest a coverage status.

## 14. Server-side dry-run pred mutation

Deploy template najprv vyrenderuje exact manifest a vykoná:

```bash
kubectl apply \
  --server-side \
  --dry-run=server \
  --namespace "$TARGET_NAMESPACE" \
  -f rendered/
```

Tento krok posiela objekty API serveru bez uloženia. Overuje aktuálnu API schema, admission policy a authorization identity pre daný cluster context.

Server-side dry-run má presnú dôkaznú hranicu. API server overil object schema, admission a caller authorization pre daný request, ale nevytvoril novú persisted generation a nespustil controller lifecycle.

Dry-run preto nepreukazuje, že Deployment controller vytvorí ready Pods ani že scheduler, kubelet a registry dokážu image pull-nuť. Nevykoná Service selector/EndpointSlice convergence, takže neukazuje, či traffic nájde backendy. Application process nevznikol, a preto nemohol načítať ConfigMap, Secret ani environment-specific configuration. Napokon neprebehol žiadny request cez reálnu route, takže business outcome zostáva úplne neoverený.

Po dry-run nasleduje reálny apply, controller/runtime read-back, exact image/config identity, Service/EndpointSlice kontrola a business probe. Ak dry-run zlyhá, mutation sa nesmie vykonať; ak prejde, je to iba povolenie pokračovať do ďalších acceptance vrstiev.

## 15. `resource_group`: serializácia environment mutation

```yaml
resource_group: payments-production
```

bráni dvom production deploy jobs meniť ten istý environment súčasne. Nevyrieši však external writera, napríklad manuálny `kubectl`, Argo CD alebo iný project s rovnakým cluster accessom.

Jeden environment potrebuje jedného autoritatívneho deployment writera alebo jasne definovanú koordináciu. Inak resource group serializuje iba GitLab jobs v tomto scope, nie celý control plane.

## 16. Rollout status a jeho proof boundary

```bash
kubectl rollout status deployment/payments-api --timeout=5m
```

Úspech preukazuje, že Deployment controller dosiahol svoj rollout success condition. Je to silnejší dôkaz než úspešný `kubectl apply`, ale stále nie business acceptance.

Nasleduje exact live-image read-back:

```bash
LIVE_IMAGE="$(kubectl get deployment payments-api \
  --namespace "$TARGET_NAMESPACE" \
  -o jsonpath='{.spec.template.spec.containers[?(@.name=="payments-api")].image}')"

test "$LIVE_IMAGE" = "$IMAGE_REFERENCE"
```

Tým overíme desired Pod template v live Deploymente. Stále nevieme, či každý running container skutočne používa túto image generation. Pri incidentnej diagnostike treba skontrolovať aj Pod specs, container statuses a runtime `imageID`.

## 17. EndpointSlice a service smoke test

```bash
kubectl get endpointslice \
  --namespace "$TARGET_NAMESPACE" \
  -l kubernetes.io/service-name=payments-api \
  -o yaml
```

EndpointSlice ukáže, ktoré backend addresses sú associated so Service a či sú marked ready. Neoveruje, že aplikácia vráti správny payload.

Smoke Pod vykoná request cez Service DNS:

```bash
curl --fail --silent --show-error http://payments-api/version
```

Očakávaný payload:

```json
{
  "service": "payments-api",
  "version": "1.0.481",
  "commit": "9f0d2c..."
}
```

Tento výsledok dokazuje funkčný path:

```text
smoke Pod
→ cluster DNS
→ Service
→ EndpointSlice/backend
→ application process
→ /version response
```

Nedokazuje external ingress, používateľskú autentizáciu, database transaction ani payment settlement. Tie patria do ďalšej acceptance vrstvy.

## 18. Staging a production používajú rovnaký artifact

Oba jobs dostanú ten istý `IMAGE_REFERENCE` z `build_image`. Líšia sa iba environment subjectom:

```text
staging:
  cluster context atlas/platform-agent:staging
  namespace payments-staging

production:
  cluster context atlas/platform-agent:production
  namespace payments-production
```

Production job je manuálny a `allow_failure: false`. Manual click je iba approval event. Dôveryhodné rozhodnutie musí byť viazané na commit, image digest, scanner/report inventory a target environment generation.

Protected environment policy má obmedziť, kto job môže spustiť. Branch protection sama o sebe nechráni production environment.

## 19. Čo uvidíme v merge-request pipeline

Pre merge request očakávame iba:

```text
validate_source
→ unit_tests
```

Over to v pipeline graph-e alebo cez jobs API. Očakávaný set neobsahuje `build_image`, `scan_image`, `staging_deploy` ani `production_deploy`.

Ak sa privileged build job objaví v merge-request pipeline, problém nie je „job zatiaľ nikto nespustil“. Resolved graph už porušuje trust contract a treba opraviť `rules`, runner protection alebo project policy.

## 20. Čo uvidíme po merge-i do default branch

Očakávaný graph:

```text
validate_source
→ unit_tests
→ build_image
→ verify_registry_subject ┐
→ scan_image              ├→ staging_deploy
                          └→ production_deploy [manual]
```

Staging a production nesmú buildovať vlastný image. Oba musia používať digest z rovnakého producer jobu.

## 21. Worked failure: zelený deployment job, nesprávny runtime image

Predstav si, že deploy script používa `$IMAGE_TAG` namiesto `$IMAGE_REFERENCE`. Build job publikuje tag na digest `D1`. Pred production approvalom iný pipeline pri chybnej registry policy prepíše ten istý tag na `D2`.

```text
scan D1 pass
→ staging používa D1
→ tag prepísaný na D2
→ production Deployment dostane tag
→ kubelet pull-ne D2
→ GitLab deployment job je green
→ production nepoužíva skenovaný artifact
```

Root cause je strata immutable artifact identity medzi buildom a deploymentom. Oprava je digest reference, write-once tag policy a live image read-back.

## 22. Worked failure: scanner job neexistuje

Chybná `rules` podmienka môže spôsobiť, že `scan_image` vôbec nevznikne. Ak `staging_deploy` nemá explicitný `needs` edge alebo pipeline gate kontroluje iba failures, deployment môže pokračovať.

```text
expected scanner = scan_image
resolved scanner jobs = none
failures = 0
```

Verdict nie je pass. Je to missing evidence. Pipeline design má pracovať s expected job/report inventory a deploy job má explicitne závisieť od scanneru.

## 23. Worked failure: rollout ready, business path chybný

Deployment môže byť ready, `/version` môže odpovedať a Service môže mať backendy, no aplikácia môže používať nesprávny database endpoint.

```text
process ready
→ network path healthy
→ /version pass
→ payment create request zlyhá
```

Pre produkciu treba pridať business-safe smoke test, napríklad idempotentný test transaction alebo read-only critical journey. Jeho side effects, cleanup a test identity musia byť explicitné.

## 24. Diagnostický postup pri zlyhaní

Pri probléme neklikaj najprv `Retry`. Stabilizuj subject:

```text
commit SHA
pipeline ID a source
resolved jobs/includes
runner ID, tags a executor
build metadata a image digest
scanner report subject
cluster context a namespace
Deployment generation
Pod imageID
EndpointSlice
smoke/business request ID
```

Potom rozlišuj hypotézy:

```text
H1: job nevznikol pre rules
H2: job bežal na nesprávnom runneri
H3: dotenv artifact sa nepreniesol
H4: tag a digest sa rozchádzajú
H5: scanner report je invalidný alebo stale
H6: cluster context smeruje na nesprávny cluster
H7: API prijalo manifest, rollout zlyhal
H8: rollout je ready, Service nemá endpointy
H9: Service funguje, business dependency zlyháva
```

Každá hypotéza má iný observation point. Rerun môže zmeniť registry tag, runner, cache alebo cluster state a zničiť pôvodné evidence.

## 25. Acceptance checklist pre walkthrough

Walkthrough je úspešne vykonaný iba vtedy, keď vieš preukázať:

```text
merge-request pipeline neobsahuje privileged/deploy jobs
+ JUnit report existuje a GitLab ho spracoval
+ default-branch build publikuje jeden image digest
+ tag resolve-ne na rovnaký digest v čase verification
+ scanner číta presne digest, ktorý sa nasadzuje
+ deploy job používa správny cluster context a namespace
+ server-side dry-run prejde
+ rollout dosiahne ready stav
+ live Deployment image sa rovná expected digest reference
+ Service má ready EndpointSlices
+ smoke request vráti expected commit
+ production používa ten istý image digest ako staging
+ druhý pipeline nevie obísť protected environment alebo prepísať artifact subject
```

Takto treba čítať GitLab pipeline ako jeden execution a evidence systém. `.gitlab-ci.yml` je iba source deklarácia. Dôveryhodný deployment vzniká až po resolve graphu, správnom runner trust contexte, immutable artifact hand-offe, environment mutation a nezávislom runtime overení.

## Primárne zdroje

- [GitLab CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [GitLab `needs`](https://docs.gitlab.com/ci/yaml/needs/)
- [GitLab job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [GitLab artifact reports](https://docs.gitlab.com/ci/yaml/artifacts_reports/)
- [GitLab environments](https://docs.gitlab.com/ci/environments/)
- [GitLab deployments](https://docs.gitlab.com/ci/environments/deployments/)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitLab CI/CD syntax](gitlab-ci-cd-syntax.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runners a executors →](runners-and-executors.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
