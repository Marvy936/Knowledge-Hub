# Ansible Idempotency

This lab teaches a common Ansible idempotency failure. The supplied playbook manages an existing application configuration file with `state: touch`, so every identical run updates file metadata and reports a change.

Repair the playbook so the file remains managed but a second identical run converges with `changed=0`. The application configuration must remain exactly `MODE=production`.

Ansible and all supporting tools run inside the Knowledge Hub lab image. The host requirement remains Docker only.

Use the built-in commands `status`, `apply`, `check`, `hint`, and `reset` while working on `/workspace/site.yml`.
