# Kubernetes Service Selector

The application Pods are healthy, but the Kubernetes Service has no usable backends. Diagnose the relationship between Pod labels, the Service selector, Endpoints, and actual Service traffic.

The cluster contains:

- Deployment `kh-web` in namespace `kh-selector` with two healthy Pods labeled `app=kh-web`;
- Service `kh-web` exposing port `80` to container port `8080`;
- a broken selector in `/workspace/service.yaml`.

Repair the Service so Kubernetes discovers the intended Pods and traffic through the Service returns exactly `selector-ok`.

Start with:

```bash
kubectl get pods -n kh-selector --show-labels
kubectl get service kh-web -n kh-selector -o yaml
kubectl get endpoints kh-web -n kh-selector
status
```

You may repair `/workspace/service.yaml` and run `apply`, or make an equivalent correct change with `kubectl`. The validator checks live cluster behavior, not one specific editing method.

Lab commands: `status`, `apply`, `check`, `hint`, `reset`.
