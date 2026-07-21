# Future Identity, ML, LLM and Intelligent Automation Roadmap

Tento dokument plánuje budúce sekcie Knowledge Hubu, ktoré sa začnú spracúvať až po dokončení aktuálnej hlavnej roadmapy. Neaktivuje nové dokumentačné sekcie a nemení súčasné učebné poradie.

Navrhované poradie:

```text
existujúca roadmapa
→ Keycloak and Identity Platform
→ Machine Learning Fundamentals
→ MLOps and ML Platforms
→ LLM and GenAI Engineering
→ AI Agents and Intelligent Automation
```

Číslovanie priečinkov je predbežné. Ak existujúce sekcie Observability, Security and Identity, SRE, Databases a GitOps získajú očakávané čísla `12` až `16`, nové sekcie môžu pokračovať ako `17` až `21`.

## Zásady návrhu

- Najprv sa vysvetlia stabilné koncepty, až potom konkrétne produkty.
- Produktová kapitola nesmie nahrádzať protokol, architektúru alebo operational model.
- Každá sekcia bude obsahovať security, observability, cost, lifecycle a troubleshooting vrstvu.
- Praktické scenáre budú oddelené v `labs/` a poruchové scenáre v `troubleshooting/`.
- ML, LLM a agentické systémy budú hodnotené cez reprodukovateľné evals, nie iba subjektívne demo výsledky.
- Deterministický workflow sa nebude bezdôvodne nahrádzať autonómnym agentom.
- Citlivé tools a agents budú používať least privilege, approval gates, audit a explicitný blast-radius model.

# Fáza 6 — Identity platformy

## Keycloak and Identity Platform

Predbežný priečinok:

```text
docs/17-keycloak-and-identity-platform/
```

Sekcia nadviaže na všeobecné témy OAuth 2.0, OpenID Connect, SAML, LDAP, Kerberos, authentication a authorization zo sekcie Security and Identity. Nebude tieto protokoly vysvetľovať od začiatku; ukáže ich konkrétnu implementáciu, prevádzku a failure modes v Keycloaku.

### Odporúčané témy

1. Keycloak architecture a responsibility boundary
2. Realm, client, user, group, role a session
3. OIDC clients, redirect URIs, scopes a PKCE
4. SAML clients, metadata, assertions a bindings
5. Tokens, claims, protocol mappers a client scopes
6. Public, confidential a bearer-only client model
7. Service accounts a machine-to-machine authentication
8. Authentication flows, executions a required actions
9. MFA, WebAuthn, passkeys a step-up authentication
10. Password policies, brute-force protection a account recovery
11. Identity brokering
12. LDAP a Active Directory federation
13. User storage, synchronization a cache semantics
14. Authorization Services, resources, scopes, policies a permissions
15. Token exchange, impersonation a delegated access
16. Admin Console, Admin REST API a automation
17. Events, audit, metrics a observability
18. Themes, email templates a localization
19. Keycloak server configuration, hostname a reverse proxy
20. TLS, truststores, cookies, headers a production hardening
21. Database, transactions, connection pools a schema lifecycle
22. Infinispan caches, clustering a session behavior
23. Keycloak Operator a Kubernetes deployment
24. High availability, multi-AZ a multi-cluster trade-offs
25. Backup, restore, realm import/export a disaster recovery
26. Upgrades, migration guides a rollback boundaries
27. Custom providers, SPI a extension lifecycle
28. Securing APIs, microservices a MCP servers cez Keycloak
29. Keycloak performance, sizing a load testing
30. Keycloak troubleshooting

### Praktická vrstva

```text
labs/keycloak/
troubleshooting/keycloak/
```

Navrhované laby:

- OIDC web application s Authorization Code + PKCE,
- service-to-service client credentials,
- LDAP/AD federation,
- external identity provider a first-broker-login flow,
- WebAuthn alebo passkey authentication,
- fine-grained authorization pre API resources,
- Keycloak na Kubernetes s PostgreSQL a Operatorom,
- upgrade a recovery rehearsal,
- zabezpečenie MCP servera cez Keycloak.

Navrhované drilly:

- redirect URI mismatch,
- invalid issuer alebo audience,
- clock skew a expired token,
- login redirect loop,
- chybný protocol mapper,
- LDAP synchronization alebo bind failure,
- reverse-proxy hostname/header problém,
- session/cache inconsistency,
- database connection exhaustion,
- failed rolling upgrade.

# Fáza 7 — Machine Learning a MLOps

## Machine Learning Fundamentals

Predbežný priečinok:

```text
docs/18-machine-learning-fundamentals/
```

Hĺbka bude orientovaná na DevOps, platform a operations rolu. Cieľom nie je úplný matematický odbor, ale schopnosť rozumieť tomu, čo sa trénuje, čo sa meria, prečo model zlyháva a čo musí MLOps platforma zachovať.

### Odporúčané témy

1. Artificial intelligence, machine learning, deep learning a generative AI
2. Dataset, sample, feature, label a target
3. Supervised, unsupervised a reinforcement learning
4. Regression, classification, ranking a clustering
5. Train, validation a test split
6. Data preprocessing, normalization a encoding
7. Feature engineering a feature selection
8. Data leakage a train-serving skew
9. Linear a logistic regression
10. Decision trees, random forests a gradient boosting
11. Neural network fundamentals
12. Loss functions a optimization
13. Gradient descent, learning rate a convergence
14. Overfitting, underfitting, bias a variance
15. Regularization a early stopping
16. Hyperparameters a hyperparameter optimization
17. Classification metrics
18. Regression metrics
19. Imbalanced datasets a threshold selection
20. Cross-validation
21. Calibration a uncertainty
22. Explainability a feature importance
23. Data quality, bias a responsible AI
24. Reproducibility a random seeds
25. Offline evaluation oproti production outcome
26. ML troubleshooting mental model

### Praktická vrstva

```text
labs/machine-learning/
```

Flagship lab:

```text
raw dataset
→ validation a preprocessing
→ baseline model
→ train/validation/test evaluation
→ experiment comparison
→ packaged inference artifact
```

## MLOps and ML Platforms

Predbežný priečinok:

```text
docs/19-mlops-and-ml-platforms/
```

### Odporúčané témy

1. ML lifecycle a rozdiel medzi DevOps a MLOps
2. Data, code, environment a model lineage
3. Dataset versioning
4. Experiment tracking
5. Artifact stores
6. Model packaging a reproducible environments
7. Model Registry, versions, stages a aliases
8. Feature stores a online/offline consistency
9. ML pipeline orchestration
10. Training pipelines a distributed training
11. CI pre ML code, data a pipelines
12. Continuous Delivery pre modely
13. Continuous Training a retraining triggers
14. Model validation a promotion gates
15. Batch, online a streaming inference
16. Shadow, canary a A/B model deployment
17. Model serving a autoscaling
18. GPU scheduling, utilization a capacity
19. Model monitoring
20. Data drift, concept drift a prediction drift
21. Performance, latency, throughput a cost monitoring
22. Feedback loops a ground-truth delay
23. Model rollback a recovery
24. Governance, approvals a audit
25. Privacy, security a adversarial ML
26. ML supply-chain security
27. MLflow experiment tracking a Model Registry
28. MLflow evaluation, tracing a deployment
29. Kubeflow Pipelines
30. Kubeflow Trainer a distributed training
31. KServe alebo ekvivalentný Kubernetes model serving
32. Amazon SageMaker a cloud MLOps mapping
33. MLOps platform architecture
34. MLOps troubleshooting

### Praktická vrstva

```text
labs/mlops/
troubleshooting/mlops/
```

Flagship projekt:

```text
Git + dataset version
→ pipeline validation
→ train a evaluate
→ MLflow tracking
→ registry promotion
→ containerized serving
→ canary deployment
→ monitoring a drift signal
→ controlled retraining
```

Navrhované drilly:

- experiment bez reprodukovateľného environmentu,
- model artifact bez lineage,
- schema drift,
- training-serving skew,
- chybný registry alias,
- failed model load,
- incompatible feature contract,
- GPU OOM alebo nízka utilization,
- false drift alert,
- rollback modelu bez rollbacku feature pipeline.

# Fáza 8 — LLM, GenAI a agentická automatizácia

## LLM and GenAI Engineering

Predbežný priečinok:

```text
docs/20-llm-and-genai-engineering/
```

### Odporúčané témy

1. Generative AI, foundation model a large language model
2. Transformer architecture na praktickej úrovni
3. Tokens, tokenization a context window
4. Embeddings a semantic similarity
5. Inference parameters, sampling a determinism
6. Prompt roles, instructions, context a examples
7. Zero-shot, one-shot a few-shot prompting
8. Prompt templates, variables a versioning
9. Prompt decomposition a chain-of-thought boundaries
10. Structured Outputs a schema validation
11. Function calling a tool calling
12. Model selection a capability/cost trade-offs
13. Model version pinning a compatibility
14. Retrieval-Augmented Generation architecture
15. Chunking, metadata a document processing
16. Vector stores a indexing
17. Retrieval, hybrid search a reranking
18. Context assembly a citation grounding
19. RAG evaluation a retrieval diagnostics
20. Fine-tuning, instruction tuning a preference tuning
21. PEFT, adapters a LoRA
22. Quantization a local inference
23. GPU memory, batching a serving performance
24. Prompt caching, semantic caching a response caching
25. LLM gateways, routing, fallback a rate limiting
26. Prompt Registry a lifecycle
27. LLM evaluation datasets a graders
28. Human evaluation a expert feedback
29. Tracing, token usage a cost observability
30. Hallucination, faithfulness a factuality
31. Prompt injection a indirect prompt injection
32. Data exfiltration, tool abuse a excessive agency
33. Guardrails, moderation a output validation
34. Privacy, retention a provider data controls
35. Multimodal models
36. LLMOps a production readiness
37. LLM application troubleshooting

### Praktická vrstva

```text
labs/llm-engineering/
troubleshooting/llm-engineering/
```

Flagship projekty:

- prompt versioning + eval-driven promotion,
- RAG nad Knowledge Hub dokumentáciou,
- structured extraction pipeline,
- model gateway s fallbackom a budget limitom,
- lokálny quantized model deployment,
- red-team test prompt injection a data leakage.

## AI Agents and Intelligent Automation

Predbežný priečinok:

```text
docs/21-ai-agents-and-intelligent-automation/
```

Sekcia začne rozdielom medzi deterministickým workflowom a agentom. Agent sa použije iba tam, kde rozhodovanie nemá jednoduchú stabilnú implementáciu pravidlami alebo klasickým kódom.

### Základné agentické témy

1. Deterministic workflow, probabilistic component a autonomous agent
2. Agent loop, state, observation, action a termination
3. Tool calling a tool contracts
4. Planning, decomposition a replanning
5. Short-term state, long-term memory a external memory
6. Single-agent a multi-agent architecture
7. Supervisor, router a specialist patterns
8. Human-in-the-loop a approval gates
9. Durable execution, retries a resumability
10. Idempotency a side-effect control
11. Model Context Protocol
12. Agent interoperability a protocol evolution
13. Agent identity, authentication a authorization
14. Least privilege pre tools a credentials
15. Sandboxing a code execution
16. Prompt injection cez tools a retrieved content
17. Tool poisoning, confused deputy a data exfiltration
18. Agent evaluation
19. Trajectory, tool-selection a outcome evaluation
20. Agent tracing, replay a debugging
21. Cost, latency a token budgets
22. Agent reliability, fallback a kill switch
23. Multi-tenant isolation
24. Agent governance a audit

### n8n

25. n8n architecture a execution model
26. Triggers, nodes, expressions a data mapping
27. Webhooks a API integrations
28. Credentials, secrets a access control
29. Error workflows, retries a partial execution
30. Idempotency a duplicate-event handling
31. Sub-workflows a reusable workflow contracts
32. Source control a environments
33. Self-hosting s PostgreSQL
34. Queue mode, Redis, workers a scaling
35. Binary data, storage a execution retention
36. n8n monitoring, logs a security audit
37. AI Agent nodes, tools a memory
38. Human approval pre citlivé tool calls
39. RAG a knowledge workflows v n8n
40. Production hardening a troubleshooting

### Harness AI a agentický DevOps

41. Harness AI platform overview
42. DevOps Agent pre pipeline a resource operations
43. Worker Agents v pipelines
44. MCP connectors a external tools
45. AI-assisted pipeline creation a failure analysis
46. Agentický code review, testing a remediation
47. GitOps a release agents
48. Incident triage a evidence collection
49. Policy generation a policy validation
50. Human approval, audit a rollback
51. Vendor lock-in a portability agentických workflowov

### Širšia automation vrstva

52. Workflow engine oproti agent frameworku
53. n8n oproti Temporal, Airflow a Prefect use cases
54. Event-driven automation
55. AI-assisted CI/CD
56. AI-assisted observability a incident response
57. AI-assisted security operations
58. Knowledge assistants a enterprise search
59. Ticket, email a chat automation
60. Autonomous remediation boundaries
61. Evaluation-driven automation lifecycle
62. Intelligent automation troubleshooting

### Praktická vrstva

```text
labs/ai-automation/
troubleshooting/ai-automation/
```

Flagship projekt:

```text
alert alebo ticket
→ deterministic enrichment
→ agentic diagnosis
→ read-only tools
→ evidence a confidence
→ human approval
→ bounded remediation tool
→ validation
→ audit trail a rollback
```

Navrhované drilly:

- agent vyberie nesprávny tool,
- tool schema nevyjadruje bezpečné constraints,
- prompt injection v dokumente alebo tickete,
- nekonečný agent loop,
- duplicated side effect po retry,
- expired credential alebo excessive permission,
- n8n queue backlog,
- worker/version mismatch,
- chýbajúci human approval,
- agent vykoná remediation bez hard validation,
- model/provider outage,
- prekročený token alebo cost budget.

# Cross-section flagship projekty

## 1. Identity-aware AI platform

```text
Keycloak
→ OIDC login
→ user/group/role claims
→ LLM application
→ RAG authorization filtering
→ audited tool calls
```

Cieľom je zabrániť tomu, aby používateľ získal cez RAG alebo agent tools prístup k dátam, ku ktorým nemá oprávnenie.

## 2. End-to-end MLOps platform

```text
Git + CI
→ dataset a feature validation
→ Kubeflow pipeline
→ MLflow tracking/registry
→ KServe deployment
→ observability
→ drift a retraining workflow
```

## 3. Knowledge Hub assistant

```text
Markdown source
→ indexing
→ retrieval + reranking
→ grounded answer s citations
→ eval dataset
→ tracing, latency a cost monitoring
```

## 4. Agentic DevOps automation

```text
CloudWatch/GitLab/Kubernetes incident
→ n8n workflow
→ agent diagnosis
→ MCP/API tools
→ approval
→ bounded remediation
→ post-change validation
```

## 5. Harness AI applied track

Použiť Harness AI ako konkrétny enterprise príklad agentickej DevOps platformy, nie ako náhradu všeobecných princípov. Porovnať:

- built-in DevOps Agent,
- Worker Agents,
- pipeline context,
- MCP connectors,
- policy a approval model,
- audit a rollback,
- portability oproti vlastnému agent workflowu.

# Odporúčané poradie realizácie

1. Dokončiť existujúcu roadmapu.
2. Dokončiť Security and Identity pred Keycloak sekciou.
3. Dokončiť Observability, Databases a GitOps pred MLOps.
4. Spracovať Machine Learning Fundamentals.
5. Spracovať MLOps and ML Platforms.
6. Spracovať LLM and GenAI Engineering.
7. Spracovať AI Agents and Intelligent Automation.
8. Až po konceptoch doplniť rozsiahle produktové laby n8n, Harness AI, MLflow, Kubeflow a cloudové ML služby.

# Navrhované zdroje

Primárne zdroje sa majú pri realizácii vždy znovu overiť, pretože tieto oblasti sa menia rýchlo.

- Keycloak Documentation: https://www.keycloak.org/documentation
- Keycloak Guides: https://www.keycloak.org/guides
- MLflow Documentation: https://mlflow.org/docs/latest/
- Kubeflow Documentation: https://www.kubeflow.org/docs/
- OpenAI Platform Documentation: https://platform.openai.com/docs/
- n8n Documentation: https://docs.n8n.io/
- Harness AI Documentation: https://developer.harness.io/docs/platform/harness-ai/overview/

# Stav

Tento plán je pripravený, ale ešte nie je súčasťou aktívnej lineárnej dokumentácie. Keď sa dokončí aktuálna roadmapa, témy sa prenesú do `ROADMAP.md`, vytvoria sa sekčné `README.md` súbory a zapoja sa do automatickej navigácie, glossary a review workflowu.
